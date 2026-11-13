# From email alerts to an assistant that follows an order through

## The problem I wanted to solve

Useful information arrives in separate places: an order confirmation, a dispatch
email, a courier page, a warehouse registration notice. Reading each message does
not automatically produce a reliable picture of what is still on the way, what
has arrived, or what needs a decision.

My initial request was selective email monitoring. I wanted information that
helped me act or avoid missing something, without routine receipts and promotions
becoming a constant stream of interruptions. I then extended the requirement:
new orders and shipping notices should enter a tracking workflow automatically,
update a readable inventory, and stop being tracked when delivery is complete.

This changed the task from summarizing messages to maintaining an ongoing process.

## How I shaped the behavior

| Decision I made | Consequence for the design |
| --- | --- |
| Alert on useful changes, not every email | Notification importance must be separate from whether a fact should be saved |
| Follow new orders and shipments without another request | Retain order identity, references, shipment legs and the next tracking work |
| Keep routine overnight updates quiet | Delivery policy needs a schedule and urgency context, not just a model-written reply |
| Use a short name for the whole order | Keep a presentation label separate from exact item titles and quantities |
| Say which source established a milestone | Preserve provenance and distinguish courier arrival from warehouse registration |
| Close tracking after actual final delivery | An intermediate destination or an old estimate must not complete the order |
| Monitoring is not permission to transact | Reading an email cannot authorize payment, cancellation, forwarding or a reply |

The specific data contracts and implementation details were proposed and written
by coding agents. My contribution was setting these expectations, assessing the
behavior in use, challenging mistakes and directing the next iteration.

## From conversational requirement to implemented workflow

The private implementation separates responsibilities:

1. **Discover and interpret.** Periodic inbox checks use retained per-account
   checkpoints. A model classifies usefulness and extracts supported order facts
   from bounded message content and relevant context.
2. **Validate and retain.** Owned code checks the extraction against source
   evidence. A durable outbox retains valid observations before applying them to
   order state. An ignored alert can still contribute a valid order fact.
3. **Maintain identity and state.** Exact references associate observations with
   orders and individual shipment legs. Inbound and onward shipping remain
   distinct. Ambiguous associations are retained for reconciliation rather than
   guessed into a match.
4. **Check progress.** Due checks read supported carrier sources and record
   evidenced milestones. A readable inventory is updated from the owned state.
5. **Notify and complete.** Policy selects useful updates, applies quiet hours
   and tracks delivery outcomes. Final delivery ends the corresponding tracking
   work; a forwarding-warehouse arrival does not.

A failed store write can retry the retained observation without repeating model
classification. An uncertain notification stays distinguishable from a confirmed
send. These are ordinary state and delivery guarantees, not reasoning performed
by the language model.

## Corrections that changed the implementation

### Arrival is not registration

An early update made a courier-reported warehouse arrival sound like warehouse
registration. I corrected that distinction. The resulting design keeps the
source and milestone explicit instead of treating every use of "arrived" as the
same state.

A fictional example of the intended wording is:

> Carrier tracking shows Lumen Studio order has arrived at the forwarding warehouse.

That sentence does not claim that the warehouse has checked in the contents or
that the final delivery is complete.

### Order names should orient me, not enumerate the contents

Full product titles were cumbersome and could make the number of items unclear.
I asked for a short order-level name, and for a model to interpret the available
retailer and item context rather than rely on an exhaustive naming list.

The implementation retains that concise label alongside the original titles,
item details and supporting evidence. It is reused for later tracking updates;
renaming the display does not merge orders or rewrite their contents.

### One blocked outcome must not stop unrelated work

Later failures showed why "the scheduled run succeeded" and "every action
completed" need separate meanings. Historical uncertain sends and downstream
order work were retained without permanently disabling otherwise healthy inbox
discovery. Fresh discovery failures still remain failures. This preserves the
unfinished work while allowing independent useful work to continue.

## What was tested and what remains uncertain

Source and historical verification records support the implemented extraction,
order-state, ledger and notification paths. Recorded acceptance includes a real
carrier-arrival observation, a ledger update and a confirmed notification.
Agents ran the automated and controlled integration checks; I supplied the
requirements and feedback from the actual messages I received.

Tests cover silent receipts, retained-write retries, separate and consolidated
shipments, conflicting updates, uncertain sends and final-delivery closure.
At the recorded lifecycle checkpoint, complete natural final-delivery closure
had fixture coverage but had not been observed end to end. This showcase does
not turn that into a production-wide reliability claim.

Extraction can still miss meaning, sites can be unavailable and evidence can be
ambiguous. Exact source quotes support provenance; they do not prove every
interpretation is correct. The feature is periodic monitoring with supported
integrations, not an instant or universal courier service.

## What the public demo makes inspectable

The [offline demo](demo/README.md) recreates a small portion with fictional data:
silent order creation, distinct shipment milestones, concise attributed updates,
completion, repeat suppression and retained uncertain delivery.

It starts after interpretation. It neither reads real email nor asks a model to
classify it. This makes the state and policy behavior reproducible without
publishing private code or pretending the small demo is the entire assistant.

The broader development lesson is the link between product judgment and technical
constraints: deciding what should happen, observing where the system gets the
meaning wrong, and directing agents to make those distinctions explicit and testable.
