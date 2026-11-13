# Assistant Showcase

**Turning everyday friction into agent workflows, then testing what they actually do.**

This is a public case study by [nyanyui](https://github.com/nyanyui) about directing
the development of a personal assistant with coding agents. I defined the desired
behavior, used the assistant, identified failures and refined the requirements.
Coding agents investigated the system, proposed technical designs, implemented
the code and ran automated checks.

## Main case: from useful email to an ongoing package workflow

I wanted an assistant that could recognize which emails mattered, remember new
orders, track their progress and tell me when something needed attention. A
stream of inbox summaries would still leave the tracking work to me.

The design evolved through use: routine receipts could update records silently;
notifications needed short whole-order names; and a courier saying a parcel had
reached a forwarding warehouse must not imply that the warehouse had registered
its contents or that the parcel had reached me.

[Read the email case study](CASE_STUDY.md) for the requirements, implementation
boundaries, corrections and evidence. The focus is connecting interpretation to
durable state and useful follow-through.

## Supporting case: preferences that reduce repeated decisions

Travel planning shows another part of the same goal: make the assistant carry
reusable preferences and planning rules, while retaining exceptions and uncertain
choices. A default party size should not require repeated clarification; a route
choice should not silently cancel a booking.

[Read the travel case and ongoing trust work](TRAVEL_CASE_STUDY.md). Implemented
travel behavior is distinguished from the separate trust research and integration
work still in progress.

## Run the synthetic package demo

Python 3.11+ is sufficient. No dependencies, account, API key or network access
are required. From the repository root:

```sh
python demo/assistant_demo.py --state .demo-state/packages.sqlite3 --scenario initial
python demo/assistant_demo.py --state .demo-state/packages.sqlite3 --scenario warehouse
python demo/assistant_demo.py --state .demo-state/packages.sqlite3 --scenario delivered
python demo/assistant_demo.py --state .demo-state/packages.sqlite3 --scenario delivered
python -m unittest discover -s tests -v
```

The fictional receipt creates an order silently. Later observations advance its
shipment milestones and produce concise, source-specific updates. Repeating the
same observations produces no repeat notification. See the [demo guide](demo/README.md)
for the individual stages and uncertain-send scenario.

This is a newly written simulation of selected mechanics. Structured fixtures
stand in for model extraction. It does not connect to Gmail, couriers or Telegram,
and it does not measure the private assistant's accuracy or production reliability.

| Document | Purpose |
| --- | --- |
| [Email case study](CASE_STUDY.md) | From user intent to a persistent order workflow |
| [Travel and trust](TRAVEL_CASE_STUDY.md) | Reusable preferences, exceptions and delegation boundaries |
| [Contributions](CONTRIBUTIONS.md) | Human direction and acceptance versus agent implementation |
| [Architecture](ARCHITECTURE.md) | Where reasoning, state and tools fit together |
| [Verification](VERIFICATION.md) | Supported claims, evidence levels and limitations |

The private assistant uses local storage and orchestration with hosted models
and external services. This repository contains no private source, Git history,
conversations, operational logs, configuration, assets or live records.
