"""Offline email-to-package teaching demo. All inputs and deliveries are synthetic."""
from __future__ import annotations

import argparse
from contextlib import closing
import hashlib
import json
from pathlib import Path
import re
import sqlite3
from typing import Callable
from urllib.parse import urlsplit


FIXTURES = Path(__file__).with_name("fixtures.json")
ID = re.compile(r"[a-z][a-z0-9-]{0,63}")
SCENARIOS = {"initial": 1, "shipped": 2, "warehouse": 3,
             "registered": 4, "forwarded": 5, "delivered": 6}
FIELDS = {"order_confirmation": {"order_name"},
          "shipment": {"tracking_ref", "destination"},
          "carrier_delivery": {"tracking_ref", "destination"},
          "warehouse_registration": {"warehouse_ref"}}
SOURCES = {"order_confirmation": {"retailer_email"},
           "shipment": {"retailer_email", "warehouse_email"},
           "carrier_delivery": {"carrier_tracking"},
           "warehouse_registration": {"warehouse_email"}}


def valid_text(value: str, limit: int) -> bool:
    return (isinstance(value, str) and bool(value.strip()) and len(value) <= limit
            and not any(ord(c) < 32 or 127 <= ord(c) <= 159 or c in "\u2028\u2029" for c in value))


def validate(document: dict) -> list[dict]:
    if not isinstance(document, dict) or set(document) != {"notice", "schema_version", "observations"}:
        raise ValueError("Expected the synthetic fixture envelope")
    if type(document["schema_version"]) is not int or document["schema_version"] != 1:
        raise ValueError("Unsupported fixture version")
    observations = document["observations"]
    if not isinstance(observations, list) or not 1 <= len(observations) <= 100:
        raise ValueError("Expected 1 to 100 observations")
    seen = set()
    for observation in observations:
        if not isinstance(observation, dict) or set(observation) != {
                "id", "order_id", "kind", "source_kind", "source_url", "facts"}:
            raise ValueError("Unexpected observation fields")
        for field in ("id", "order_id"):
            if not isinstance(observation[field], str) or not ID.fullmatch(observation[field]):
                raise ValueError("Invalid observation/order ID")
        if observation["id"] in seen:
            raise ValueError("Duplicate observation ID in input")
        seen.add(observation["id"])
        kind, facts = observation["kind"], observation["facts"]
        if not isinstance(kind, str) or kind not in FIELDS or not isinstance(facts, dict) or set(facts) != FIELDS[kind]:
            raise ValueError("Unknown kind or unexpected extracted fields")
        if not isinstance(observation["source_kind"], str) or observation["source_kind"] not in SOURCES[kind]:
            raise ValueError("Source kind cannot establish this event")
        if not valid_text(observation["source_url"], 2000):
            raise ValueError("Invalid fixture URL")
        url = urlsplit(observation["source_url"])
        if url.scheme != "https" or url.netloc != "example.invalid" or url.fragment or url.query:
            raise ValueError("Only synthetic example.invalid URLs are allowed")
        if any(not valid_text(value, 80) for value in facts.values()):
            raise ValueError("Invalid extracted fact")
        if "destination" in facts and facts["destination"] not in {"forwarding_warehouse", "final_destination"}:
            raise ValueError("Unknown destination role")
    return observations


def load_fixture(scenario: str) -> list[dict]:
    document = json.loads(FIXTURES.read_text(encoding="utf-8"))
    return validate(document)[:SCENARIOS[scenario]]


def fingerprint(observation: dict) -> str:
    return hashlib.sha256(json.dumps(observation, sort_keys=True).encode()).hexdigest()


def apply_observation(db: sqlite3.Connection, observation: dict) -> str | None:
    """Apply explicit source roles; this does not authenticate or interpret a real source."""
    previous = db.execute("SELECT fingerprint FROM observations WHERE id=?", (observation["id"],)).fetchone()
    if previous:
        if previous[0] != fingerprint(observation):
            raise ValueError("Observation ID reused with changed evidence")
        return None
    order_id, kind, source = observation["order_id"], observation["kind"], observation["source_kind"]
    facts = observation["facts"]
    row = db.execute("SELECT * FROM orders WHERE id=?", (order_id,)).fetchone()
    message = None
    if kind == "order_confirmation":
        if row:
            raise ValueError("Existing order cannot be recreated by a new confirmation ID")
        order = dict(id=order_id, name=facts["order_name"], status="ordered", case_open=1,
                     tracking_active=0, warehouse_registered=0, tracking_ref=None,
                     destination=None, warehouse_ref=None)
    else:
        if not row:
            raise ValueError("Observation refers to an unknown order")
        order = dict(row)
        if not order["case_open"]:
            raise ValueError("A closed order requires reconciliation before another transition")
        if kind == "shipment":
            inbound = facts["destination"] == "forwarding_warehouse"
            expected = ("ordered", "retailer_email") if inbound else ("registered", "warehouse_email")
            if (order["status"], source) != expected:
                raise ValueError("Shipment conflicts with the recorded stage/source")
            order.update(status="shipped" if inbound else "forwarded", tracking_active=1,
                         tracking_ref=facts["tracking_ref"], destination=facts["destination"])
            message = (f"Retailer email says {order['name']} has shipped." if inbound else
                       f"Warehouse email says {order['name']} has been forwarded to the final destination.")
        elif kind == "carrier_delivery":
            if (not order["tracking_active"] or order["tracking_ref"] != facts["tracking_ref"]
                    or order["destination"] != facts["destination"]):
                raise ValueError("Carrier evidence does not match the active parcel and destination")
            order["tracking_active"] = 0
            if facts["destination"] == "forwarding_warehouse":
                order["status"] = "at_warehouse"
                message = f"Carrier tracking shows {order['name']} has arrived at the forwarding warehouse."
            else:
                order.update(status="delivered", case_open=0)
                message = f"Carrier tracking shows {order['name']} was delivered to the final destination. Tracking is closed."
        elif kind == "warehouse_registration":
            if order["status"] != "at_warehouse":
                raise ValueError("Warehouse registration is out of sequence")
            order.update(status="registered", warehouse_registered=1, warehouse_ref=facts["warehouse_ref"])
            message = f"Warehouse email confirms {order['name']} is registered in storage."
    db.execute("""INSERT OR REPLACE INTO orders VALUES
        (:id,:name,:status,:case_open,:tracking_active,:warehouse_registered,:tracking_ref,:destination,:warehouse_ref)""", order)
    db.execute("INSERT INTO observations VALUES (?, ?, ?)",
               (observation["id"], order_id, fingerprint(observation)))
    if message:
        db.execute("INSERT INTO notifications VALUES (?, ?, 'reserved')", (observation["id"], message))
    return message


def run(observations: list[dict], state: Path, *, simulate_uncertain: bool = False,
        emit: Callable[[str], None] = print) -> dict:
    validate({"notice": "Synthetic observations", "schema_version": 1, "observations": observations})
    state = Path(state)
    state.parent.mkdir(parents=True, exist_ok=True)
    with closing(sqlite3.connect(state, timeout=5)) as db, db:
        db.row_factory = sqlite3.Row
        db.executescript("""
            CREATE TABLE IF NOT EXISTS orders (
                id TEXT PRIMARY KEY, name TEXT NOT NULL, status TEXT NOT NULL,
                case_open INTEGER NOT NULL, tracking_active INTEGER NOT NULL,
                warehouse_registered INTEGER NOT NULL, tracking_ref TEXT,
                destination TEXT, warehouse_ref TEXT);
            CREATE TABLE IF NOT EXISTS observations (
                id TEXT PRIMARY KEY, order_id TEXT NOT NULL, fingerprint TEXT NOT NULL);
            CREATE TABLE IF NOT EXISTS notifications (
                observation_id TEXT PRIMARY KEY, message TEXT NOT NULL,
                status TEXT NOT NULL CHECK(status IN ('reserved','delivered','uncertain')));
        """)
        db.execute("BEGIN IMMEDIATE")
        pending = []
        for observation in observations:
            message = apply_observation(db, observation)
            if message:
                pending.append((observation["id"], message))
        db.commit()
        status = "quiet"
        if pending:
            status = "uncertain"
            try:
                emit("SIMULATED NOTIFICATIONS (no message is sent)\n" +
                     "\n".join("- " + message for _, message in pending))
                if not simulate_uncertain:
                    status = "delivered"
            finally:
                db.executemany("UPDATE notifications SET status=? WHERE observation_id=?",
                               [(status, observation_id) for observation_id, _ in pending])
                db.commit()
        held = db.execute("SELECT count(*) FROM notifications WHERE status IN ('reserved','uncertain')").fetchone()[0]
        orders = [dict(row) for row in db.execute("SELECT * FROM orders ORDER BY id")]
    return {"status": "held" if held and not pending else status,
            "notifications": len(pending), "held": held, "orders": orders}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--state", type=Path, default=Path(".demo-state/packages.sqlite3"),
                        help="Demo-only state file, never a production database")
    parser.add_argument("--scenario", choices=SCENARIOS, default="initial")
    parser.add_argument("--simulate-uncertain", action="store_true",
                        help="Pretend notification acknowledgement was lost; never blindly replay it")
    args = parser.parse_args()
    observations = load_fixture(args.scenario)
    print(f"Input: {len(observations)} synthetic structured observations; extraction and naming are supplied.")
    result = run(observations, args.state, simulate_uncertain=args.simulate_uncertain)
    print("Outcome: " + json.dumps(result, sort_keys=True))
    if result["held"]:
        print("Uncertain notification receipts require reconciliation; the demo never automatically retries them.")


if __name__ == "__main__":
    main()
