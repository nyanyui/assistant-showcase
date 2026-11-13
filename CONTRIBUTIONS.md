# Human direction and coding-agent implementation

This project demonstrates AI-assisted product and systems development. I do not
claim to have independently authored the whole software stack.

| Work | My contribution | Coding agents' contribution |
| --- | --- | --- |
| Product direction | Defined what work the assistant should take over and what useful results look like | Explored feasibility and proposed technical approaches |
| Email workflow | Set relevance, quiet-hours and follow-through requirements; expanded alerts into order tracking | Built extraction, validation, persistent state, carrier adapters and delivery handling |
| Email corrections | Challenged long item titles and the misleading equivalence of arrival and registration | Implemented grounded whole-order names, distinct milestones and attributed wording |
| Travel knowledge | Chose reusable preferences, trip/day organization, shared places and retained alternatives | Designed concrete record schemas, retrieval, update tools and agent procedures |
| Travel evaluation | Used the assistant during a trip and requested a review of what it recorded | Audited omissions, implemented checked updates and tested revised procedures |
| Trust direction | Set the goal of making delegation reflect my preferences and limits; directed ongoing trust work | Implemented and tested scoped mechanisms; remaining integration and acceptance are stated separately |
| Verification | Exercised the product, reviewed outputs and reported failures | Wrote and ran automated checks, controlled trials and deployment verification |
| Prioritization | Chose which problems to solve, constrained background activity and deferred lower-value work | Implemented selected changes and documented limits |

User feedback, an automated test and a deployment check establish different
things. A complaint about misleading wording demonstrates hands-on evaluation;
it does not mean I wrote the resulting parser or ran its test suite. Historical
agent-run checks are not presented as my personal testing or as fresh public
benchmarks.

## This public repository

I chose email as the main case and travel/preferences as the supporting case,
required honest attribution and technical verification, and prohibited exporting
private source, history or data. Coding agents prepared the prose and wrote the
standalone synthetic demo and tests for my review.

The narrative is a new summary, not a transcript export. The demo is newly written,
not a redacted copy of private modules. OpenClaw, model providers, Telegram and
the underlying platforms are external components, not systems I claim to have
invented or implemented.
