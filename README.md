<p align="center">
  <img src="assets/hero.svg" width="900" alt="Assistant Showcase: Arrived is not delivered. A personal agent that follows through.">
</p>

<p align="center">
  <a href="#see-it-work">Run the demo</a> · <a href="CASE_STUDY.md">Read the case study</a> · <a href="VERIFICATION.md">Check the evidence</a>
</p>

## The mistake that changed the design

My assistant reported a parcel as checked in when the courier had only dropped it at a forwarding warehouse. I caught it in daily use and defined what evidence should count at each step. Coding agents implemented the workflow; I tested its behavior and directed the fixes.

| What the assistant sees | What it does |
| --- | --- |
| Courier reports warehouse arrival | Mark the inbound leg complete. **Keep the order open.** |
| Warehouse confirms registration | Record a separate milestone. The order is still open. |
| Courier confirms final delivery | **Close tracking.** |
| The same evidence arrives again | **Send zero new alerts.** |

## See it work

Run both lines against a fresh demo state file. Python 3.11+; no dependencies or keys.

```sh
python demo/assistant_demo.py --state .demo-state/showcase.sqlite3 --scenario delivered
python demo/assistant_demo.py --state .demo-state/showcase.sqlite3 --scenario delivered
```

The first run closes the order. The second reports `"notifications": 0`. The offline demo uses fictional data and sends no messages. In the live assistant, carrier arrival, a ledger update, and a notification were verified together; that check did not establish full end-to-end final delivery.

[Lost-acknowledgement demo](demo/README.md#try-uncertain-delivery) · [Architecture](ARCHITECTURE.md) · [Travel preferences and trust research](TRAVEL_CASE_STUDY.md) · [Contributions](CONTRIBUTIONS.md)
