# Verification and claim boundaries

Reviewed against targeted private implementation files and project records in
November 2026. Private evidence remains private. The public demo is independently
runnable, but this repository does not reproduce the entire private assistant.

| Claim | Evidence inspected | Boundary |
| --- | --- | --- |
| Useful email alerts and saved order facts are separate decisions | Mail/order worker, policy, state tests and owning documentation | The model's semantic interpretation can still be wrong |
| Order tracking retains distinct shipment milestones | Order transitions, carrier integration and historical acceptance records | Carrier arrival is not warehouse registration or final delivery |
| Concise names are presentation labels, not replacement item records | Naming contract, validation and recorded rollout checks | Names are not always inferred correctly; original facts remain necessary |
| Routine receipts can update records silently and retained writes can retry | Worker tests and outbox/store ownership | This does not guarantee every useful message is recognized |
| Uncertain notifications remain separate from confirmed sends | Delivery policy, failure tests and retained-claim repair records | External delivery is not guaranteed exactly once |
| A real arrival, ledger update and notification were verified | Recorded controlled acceptance of the private workflow | Complete natural final-delivery closure was not observed at that lifecycle checkpoint |
| Travel preferences, alternatives and bookings have distinct meanings | Travel skill, schema, tools, change records and regression tests | Valid structure does not prove every conversational fact was captured |
| Scoped trust is implemented as a separate prototype | Local trust code, tests and recorded offline build results | Native integration and broad live acceptance remain separate |
| The user directed and tested behavior while agents implemented code | Design decisions, corrections and acceptance reports | Automated and deployment checks are attributed to the agents |
| The public example demonstrates selected state and delivery rules | Fresh source, fictional fixtures and included tests | No live model, inbox, carrier page or messaging service is exercised |

The review used owning code and test assertions, not only project-summary claims.
Historical private test counts are not presented as coverage of this public repo.
Run the reproducible tests with:

```sh
python -m unittest discover -s tests -v
```

## Public package acceptance

On 13 November 2026, the separate local showcase package passed all 12 tests
under Python 3.13.2 on Windows. Ten CLI runs also checked the individual shipment
stages, replay after closure, retained uncertain delivery across runs and a full
timeline from fresh state. These used disposable synthetic databases.

Relative document links, the explicit 11-file inventory and targeted private-data
checks passed. A separate coding agent reviewed the prose and demo for claim
accuracy, attribution, privacy and behavior. No private runtime, hosted model or
external service was exercised for this package verification. Other operating
systems and Python versions were not tested.

## Limits retained in the story

- The private assistant uses hosted reasoning and external services. Local storage
  and orchestration do not make the whole assistant offline.
- The public demo does not evaluate extraction accuracy, importance classification,
  naming quality, latency, token use, quiet-hours scheduling or live delivery.
- Unknown send outcomes are held instead of blindly replayed. A hold may leave an
  update undelivered until someone reconciles it; silence is not proof of success.
- Trust research is separate ongoing work. Neither the public demo nor the travel
  case establishes universal preference capture or completed trust integration.
- No new claim of model-weight training, measured productivity savings or complete
  autonomy is made.

## Public/private separation

This repository starts with its own Git history. Its files were newly authored
for the showcase. No private source, commits, real records, screenshots, assets,
service configuration, conversation excerpts, credentials or runtime logs are
included. Fictional fixtures use non-live example links.

The local pre-publication review checks the explicit file inventory, relative
links, targeted sensitive-data patterns, tests and staged Git diff. It is a
point-in-time review, not a guarantee about future contributions.
