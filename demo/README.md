# Offline email-to-package demo

This is freshly written teaching code, not an export of the private assistant.
Every input is fictional. All reference URLs use `example.invalid`; the program
makes no network requests or model calls and sends no messages.

Python 3.11 or newer is sufficient. From the repository root:

```sh
python demo/assistant_demo.py --state .demo-state/packages.sqlite3 --scenario initial
python demo/assistant_demo.py --state .demo-state/packages.sqlite3 --scenario shipped
python demo/assistant_demo.py --state .demo-state/packages.sqlite3 --scenario warehouse
python demo/assistant_demo.py --state .demo-state/packages.sqlite3 --scenario registered
python demo/assistant_demo.py --state .demo-state/packages.sqlite3 --scenario forwarded
python demo/assistant_demo.py --state .demo-state/packages.sqlite3 --scenario delivered
python demo/assistant_demo.py --state .demo-state/packages.sqlite3 --scenario delivered
python -m unittest discover -s tests -v
```

Each scenario supplies the timeline up to that step. Known observations are
skipped, so a later scenario also works with a fresh demo state file. The repeated
final command produces no new notification and does not change the closed order.

| Step | State change | Simulated notification |
| --- | --- | --- |
| Initial routine order confirmation | Create an order; case open, no parcel tracking yet | None |
| Retailer shipment email | Track the inbound parcel | Retailer email says the order has shipped |
| Carrier arrival at forwarding warehouse | Finish the inbound tracking leg; keep the case open | Carrier tracking shows arrival at the warehouse |
| Warehouse registration email | Record separate registration evidence | Warehouse email confirms registration in storage |
| Warehouse forwarding email | Start a different parcel's final tracking leg | Warehouse email says the order has been forwarded |
| Carrier final delivery | Stop tracking and close the order case | Carrier tracking shows delivery to the final destination |

Warehouse arrival never implies warehouse registration or final delivery. Messages
use the short, supplied order name and identify the source of each claim, without
listing individual items or exposing tracking references in notification prose.
The final JSON state is diagnostic output for this teaching example.

## Try uncertain delivery

Use a separate state file:

```sh
python demo/assistant_demo.py --state .demo-state/uncertain.sqlite3 --scenario shipped --simulate-uncertain
python demo/assistant_demo.py --state .demo-state/uncertain.sqlite3 --scenario shipped
```

The first command prints a simulated notification but pretends its acknowledgement
was lost. The second retains the uncertain receipt and does not resend it. An
interrupted reservation is also held. Later distinct observations can update the
order and produce their own notifications; older uncertainty remains visible.
There is deliberately no automatic reset or reconciliation command. Use a new
demo state filename for a fresh experiment.

## What is implemented

The fixture is validated, then explicit source and destination roles drive a small
state machine. Tracking evidence must match the current parcel and destination.
Order state, consumed observation IDs and notification reservations are committed
together to SQLite before simulated delivery. Exact replays are ignored; reuse of
an observation ID with different evidence is rejected. Notifications have separate
reserved, delivered and uncertain states.

The local SQLite file holds only demo operational state. This is not a reproduction
of the production knowledge-base storage format or every production integration.

## What is supplied or omitted

Email extraction, importance judgment, source authenticity, order matching,
destination interpretation and the short order name are pre-authored in the
fixture. The demo does not perform semantic extraction or ranking, validate real
courier responses, poll websites, access Gmail, invoke a model, update a live
forwarding ledger or send Telegram notifications. Source-kind validation checks
internal consistency only; it does not prove that real-world evidence is true.

The workflow intentionally supports one simple forwarding journey. Split parcels,
returns, cancellations, partial arrivals, out-of-order discovery, corrections and
reconciliation require additional production policy. Invalid sequences stop
without partially applying that batch. No scheduler is included.

This is not an exactly-once external delivery guarantee. Uncertain delivery needs
destination evidence to reconcile. The demo holds ambiguity instead of blindly
retrying. Use a new demo-only state file, never a production database.
