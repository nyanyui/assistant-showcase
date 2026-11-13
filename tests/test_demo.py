"""Disposable synthetic tests. No network, model, account or production state."""
from contextlib import closing
from copy import deepcopy
import importlib.util
from pathlib import Path
import sqlite3
import subprocess
import sys
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "demo/assistant_demo.py"
spec = importlib.util.spec_from_file_location("assistant_demo", SCRIPT)
demo = importlib.util.module_from_spec(spec)
spec.loader.exec_module(demo)


class DemoTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.state = Path(self.temp.name) / "packages.sqlite3"
        self.output = []

    def run_demo(self, scenario="initial", **kwargs):
        return demo.run(demo.load_fixture(scenario), self.state, emit=self.output.append, **kwargs)

    def test_routine_receipt_creates_order_silently(self):
        result = self.run_demo()
        self.assertEqual(result["notifications"], 0)
        self.assertEqual(self.output, [])
        self.assertEqual(result["orders"][0]["status"], "ordered")
        self.assertEqual(result["orders"][0]["tracking_active"], 0)
        self.assertEqual(result["orders"][0]["case_open"], 1)

    def test_shipping_starts_tracking_with_order_level_wording(self):
        result = self.run_demo("shipped")
        self.assertEqual(result["notifications"], 1)
        self.assertEqual(result["orders"][0]["tracking_ref"], "tracking-demo-inbound")
        self.assertEqual(result["orders"][0]["tracking_active"], 1)
        self.assertIn("Retailer email says Lumen Studio order has shipped.", self.output[0])
        self.assertNotIn("example.invalid", self.output[0])

    def test_carrier_arrival_is_neither_registration_nor_final_delivery(self):
        self.run_demo("shipped")
        result = self.run_demo("warehouse")
        order = result["orders"][0]
        self.assertEqual((order["status"], order["warehouse_registered"], order["case_open"]),
                         ("at_warehouse", 0, 1))
        self.assertEqual(order["tracking_active"], 0)
        self.assertIn("Carrier tracking shows Lumen Studio order has arrived at the forwarding warehouse.", self.output[-1])
        self.assertNotIn("registered", self.output[-1])
        self.assertNotIn("final destination", self.output[-1])

    def test_registration_requires_separate_warehouse_evidence(self):
        self.run_demo("warehouse")
        result = self.run_demo("registered")
        self.assertEqual(result["notifications"], 1)
        self.assertEqual(result["orders"][0]["warehouse_registered"], 1)
        self.assertEqual(result["orders"][0]["warehouse_ref"], "storage-demo-lumen")
        self.assertEqual(result["orders"][0]["case_open"], 1)
        self.assertIn("Warehouse email confirms", self.output[-1])

    def test_forwarding_tracks_new_leg_and_final_delivery_closes_case(self):
        self.run_demo("registered")
        forwarded = self.run_demo("forwarded")["orders"][0]
        self.assertEqual((forwarded["tracking_ref"], forwarded["tracking_active"]), ("tracking-demo-final", 1))
        delivered = self.run_demo("delivered")["orders"][0]
        self.assertEqual((delivered["status"], delivered["tracking_active"], delivered["case_open"]), ("delivered", 0, 0))
        self.assertIn("Carrier tracking shows", self.output[-1])
        self.assertIn("final destination. Tracking is closed.", self.output[-1])

    def test_replay_does_not_reannounce_or_regress_closed_state(self):
        self.run_demo("delivered")
        self.assertEqual(self.run_demo("delivered")["notifications"], 0)
        result = self.run_demo("initial")
        self.assertEqual(result["orders"][0]["status"], "delivered")
        self.assertEqual(len(self.output), 1)

    def test_uncertainty_survives_restart_without_blind_replay(self):
        args = [sys.executable, "-B", str(SCRIPT), "--state", str(self.state), "--scenario", "shipped"]
        first = subprocess.run(args + ["--simulate-uncertain"], capture_output=True, text=True, check=True)
        second = subprocess.run(args, capture_output=True, text=True, check=True)
        self.assertIn('"status": "uncertain"', first.stdout)
        self.assertIn('"status": "held"', second.stdout)
        self.assertNotIn("SIMULATED NOTIFICATIONS", second.stdout)

    def test_output_failure_and_interrupted_reservation_remain_held(self):
        def fail(_text):
            raise OSError("Synthetic output failure")
        with self.assertRaisesRegex(OSError, "Synthetic"):
            demo.run(demo.load_fixture("shipped"), self.state, emit=fail)
        self.assertEqual(self.run_demo("shipped")["status"], "held")
        with closing(sqlite3.connect(self.state)) as db, db:
            db.execute("UPDATE notifications SET status='reserved'")
        self.assertEqual(self.run_demo("shipped")["status"], "held")
        self.assertEqual(self.output, [])

    def test_changed_observation_id_reuse_is_rejected(self):
        self.run_demo("shipped")
        changed = demo.load_fixture("shipped")
        changed[-1]["facts"]["tracking_ref"] = "tracking-demo-other"
        with self.assertRaisesRegex(ValueError, "reused with changed evidence"):
            demo.run(changed, self.state, emit=self.output.append)
        self.assertEqual(self.run_demo("shipped")["orders"][0]["tracking_ref"], "tracking-demo-inbound")

    def test_wrong_parcel_or_destination_cannot_complete_current_tracking(self):
        self.run_demo("shipped")
        for field, value in [("tracking_ref", "tracking-demo-other"), ("destination", "final_destination")]:
            rows = demo.load_fixture("warehouse")
            rows[-1]["facts"][field] = value
            with self.subTest(field=field), self.assertRaisesRegex(ValueError, "does not match"):
                demo.run(rows, self.state, emit=self.output.append)
            self.assertEqual(self.run_demo("shipped")["orders"][0]["tracking_active"], 1)

    def test_bad_sequence_rolls_back_new_observations(self):
        self.run_demo("initial")
        rows = demo.load_fixture("registered")
        del rows[-2]
        with self.assertRaisesRegex(ValueError, "out of sequence"):
            demo.run(rows, self.state, emit=self.output.append)
        self.assertEqual(self.run_demo("initial")["orders"][0]["status"], "ordered")
        self.assertEqual(self.output, [])

    def test_invalid_source_ids_and_raw_text_fail_before_creating_state(self):
        original = demo.load_fixture("warehouse")
        mutations = [
            lambda rows: rows.append(deepcopy(rows[0])),
            lambda rows: rows[0].update(kind="unknown"),
            lambda rows: rows[-1].update(source_kind="warehouse_email"),
            lambda rows: rows[0]["facts"].update(order_name="Name\n- Forged alert"),
            lambda rows: rows[0].update(source_url="https://example.invalid/mail/x\n- Forged alert"),
            lambda rows: rows[0].update(source_url="https://example.invalid/mail/x\tcontrol"),
            lambda rows: rows[0].update(source_url="https://example.invalid/mail/x\x1bcontrol"),
            lambda rows: rows[0].update(source_url="https://real-site.example/mail/x"),
        ]
        for mutate in mutations:
            rows = deepcopy(original)
            mutate(rows)
            with self.subTest(mutation=mutate), self.assertRaises(ValueError):
                demo.run(rows, self.state, emit=self.output.append)
            self.assertFalse(self.state.exists())


if __name__ == "__main__":
    unittest.main()
