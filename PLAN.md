# Attendance project plan

Revision: 7

Updated: 9 November 2026, Europe/London

Phase: planning. No attendance prototype or model results have been verified.

## Goal and current scope

Project: Efficiently taking attendance in large lectures using student ID cards and computer vision.

The user's first milestone is to analyse an entrance recording, identify presented student ID cards and produce attendance records. The meeting and observations reported by the user are recorded in `REPORT.md`, Entry 3. Technical options in `INITIAL_RESEARCH.md` are proposals, not measured results.

| ID | Requirement or boundary | Basis |
| --- | --- | --- |
| R1 | Identify students from presented cards in recorded lecture entrance footage | User's stated first goal |
| R2 | Allow several visible cards in one frame | User reported students entering together |
| R3 | Produce an attendance result for a lecture | User's stated goal; exact format remains open |
| R4 | Record accepted IDs once per lecture; leave unreadable or conflicting observations unresolved | Proposed handling from initial research, pending confirmation |
| R5 | Compare the result with a manually checked reference and retain evidence of errors | Proposed evaluation requirement |
| R6 | Maintain a plain English activity report without hyphens in ordinary phrases | User's explicit reporting and writing preferences |

Face comparison, identifying a person from their face, checks against borrowed cards, live iPad deployment and an attendance dashboard are deferred. They are not required to test the first card reading milestone. No specific model, OCR package, deadline or accuracy threshold is agreed.

## Evidence and open questions

Current source checks: existing project report and research notes read on 9 November 2026. The top level listing contains the existing code fragment, `.venv` and documentation. It does not establish that usable footage is available elsewhere. `git status` reported that this folder is not a Git repository.

| ID | Question or assumption | Present evidence | Smallest next check |
| --- | --- | --- | --- |
| Q1 | What card feature identifies the student: printed number, barcode or something else? | Not confirmed | Inspect a permitted sample and confirm with Ody |
| Q2 | Are card details readable at the original video resolution? | User reported footage review; assistant has not inspected it | View a short original clip and representative card crops |
| Q3 | What card designs and student number formats exist? | Not confirmed | Inspect representative examples |
| Q4 | Is a class list available, and can it be used for validation? | Not confirmed | Confirm availability and expected fields |
| Q5 | What output, lecture identifier, deadline and acceptable error rates does the professor expect? | Not confirmed | Prepare a short set of questions for the next discussion |
| Q6 | How should unresolved readings be checked by a person? | Research proposal only | Agree the review result and handling with Ody |

Do not treat a guessed identifier, an OCR score or a matching class list entry as proof of a correct reading. This baseline establishes evidence that a card was presented, not that its owner was present. Failure to read a card is not proof of absence.

## Proposed information structure for the future prototype

This schema is a planning proposal. No database, dataset or export has been created. Keep small local files initially; choose formats after checking samples and output requirements.

| Record | Minimum proposed fields | Purpose |
| --- | --- | --- |
| Lecture | lecture_id, recording reference | Keep different lectures separate |
| Frame | frame_id, lecture_id, video timestamp | Trace an observation to the recording |
| Card observation | observation_id, frame_id, card region, crop reference | Represent several separate cards in the same frame |
| Reading | observation_id, raw reading, normalized identifier, method, optional tool score, review status | Keep uncertain readings visible; do not treat a tool score as a calibrated probability |
| Attendance | lecture_id, accepted identifier, first accepted timestamp, supporting observation references, decision method | Produce one result per accepted identifier per lecture |
| Reference label | observation or lecture reference, manually checked identifier or unreadable label, checker, version | Evaluate results against independently checked labels |
| Experiment | sample manifest, method configuration or version, outputs, errors and actual checks | Trace each claimed result to the inputs and method used |

Keep manual reference labels separate from predictions. Later experiments should record their source sample, pipeline settings or version, outputs, errors and actual checks. The evaluation clip should be separate from clips used to tune the approach. Use anonymous sample references in planning records; keep any raw student data in the approved project data location once one is established.

## Full roadmap and checks

| Stage | Purpose | Evidence needed to move on |
| --- | --- | --- |
| S1. Clarify the first milestone | Lead records the working deliverable, constraints and unresolved requirements | Brief drafted; identifier, output and acceptance questions remain open |
| S2. Inspect input evidence | Investigator inventories available recordings and card layouts, then checks readability and coverage | Referenced original samples and actual limitations; blocked until samples are available |
| S3. Design the first experiment | Technical planner proposes records and a small procedure; can draft while S2 is blocked | Proposal drafted; actual identifier route and input assumptions remain to be confirmed |
| S4. Team challenge and lead review | Check S1 to S3 for necessity, evidence, alternatives and failure cases | Desk review recorded; final experiment acceptance needs sample findings and required decisions |
| S5. Establish a card reading baseline | After a scoped experiment is authorized, use S2's checked samples and test the appropriate reader on manual card crops | Exact identifier results and failures; assess against agreed numerical targets |
| S6. Handle multiple cards in video | Add automatic card finding, useful crop preparation, repeated observations and attendance consolidation | Checked clip handles simultaneous cards, repeated appearances and unresolved readings |
| S7. Evaluate separate footage | Freeze the tested configuration and evaluate on footage separate from tuning | Correct, wrong, missed and unresolved identifiers, duplicate records and processing time against a checked reference |
| S8. Package evidence and findings | Assemble method, inputs, configuration, results, limitations, reproducible instructions and demonstration | A reader can trace claims to actual checks; lead assesses against agreed requirements |

These are dependencies, not calendar commitments. Numerical success targets need agreement before declaring a milestone passed. A small measured baseline can inform those targets. If input readability is poor, return to recording conditions or scope before committing to a larger model.

The first reading method depends on Q1: printed text may suggest OCR, while a barcode or another feature may need a different route. No method is selected yet. The initial inspection can use the previously suggested 20 to 30 representative original frames, with every visible card noted separately. That is a starting sample proposal, not a validated dataset size.

Repeated frames of the same card do not create more independent students. Record observation level counts and distinct lecture/student outcomes with explicit denominators. Keep manually checked labels separate from predictions, retain original samples and compare raw and normalized identifiers. A class list match alone does not establish a correct reading.

The activity report continues during all stages. S8 is the final evidence package rather than the first time documentation is written. Later implementation stages require a separately scoped development or experiment assignment.

## Current task board

Role ownership below describes responsibility. A role without an actual agent ID is not a running agent.

| Task | Deliverable and reason it is needed | Owner | Status | Dependency or acceptance check |
| --- | --- | --- | --- | --- |
| P01 | Define lead, ownership and update rules to prevent competing plans | Main assistant | done | Skill validator passed; independent read only scenario trial completed; P06 state corrected and result accepted |
| P02 | Clarify first milestone requirements and prepare unresolved questions | Planning lead | done | Working milestone, R1 to R6 and Q1 to Q6 documented; actual agreement remains in P06 |
| P03 | Propose data records, technical options and smallest first experiment | `/root/roadmap_technical` | done | Lead accepted the document based proposal on 9 November; identifier route, sample properties and numerical targets remain unconfirmed |
| P04 | Check P02 and P03 for necessity, evidence and evaluation gaps | Planning lead | blocked | Desk review completed and proposal incorporated; final experiment acceptance waits for S2 sample evidence and required P06 decisions |
| P05 | Inventory and inspect sample footage, card layouts and readable identifiers | Data investigator, unassigned; Ody supplies access | blocked | Requires available permitted footage or sample frames; return actual observations and coverage gaps without selecting a pipeline |
| P06 | Agree prototype output and evaluation expectations | Ody and professor | blocked | Requires answers not present in the current records; the question list is documented through completed task P02 |

P02 and P03 planning deliverables are complete; no professor agreement or empirical result is implied. The lead's desk review accepted a provisional experiment design, while full P04 acceptance remains blocked on input evidence and necessary decisions. Do not report P05 as complete from documents alone.

When P05 inputs become available, the investigator supplies observations to inform P03. The technical planner updates affected proposals, and the lead repeats only the affected P04 checks. P05 produces sample findings rather than OCR predictions or system design.

## Decisions and necessity checks

| ID | Decision | Reason | Reconsider when |
| --- | --- | --- | --- |
| D1 | Use one lead as the shared writer; workers return findings | Avoid competing updates and duplicate ownership | Actual workflow needs separate artifacts with explicit owners |
| D2 | Update on meaningful events during a bounded planning cycle | Keep the record current without idle loops or duplicate summaries | Ody explicitly requests a separate scheduled workflow |
| D3 | Keep card identification as the first milestone | Matches the user's current goal and tests the key uncertainty early | Ody changes scope or the first milestone is evaluated |
| D4 | Keep model training and package selection undecided | Card readability and identifier format are unconfirmed | Representative samples establish what is needed |
| D5 | Use existing files plus this plan and the team protocol | Enough structure to coordinate initial work | Proven volume or query needs justify a separate store |
| D6 | Combine scope planning with the lead role | Ody identified that requirements and task necessity belong to the lead; avoids an unnecessary handoff | Requirements work becomes a distinct specialist investigation with a concrete need |
| D7 | Give routine review and acceptance to the lead; replace the standing reviewer with a data investigator when samples support useful work | Ody questioned the overlap; separates decisions, proposed methods and actual input observations | A specific decision needs additional expertise beyond the current team |
| D8 | Allow direct challenge and debate, including disagreement with the lead; escalate unresolved material decisions to Ody | Ody explicitly wants a team that can argue and come back to him when it cannot resolve an issue | Ody changes the team's decision process |
| D9 | Require ongoing direct communication, partial findings, checkpoints and acknowledgement of material changes during active work | Ody asked for all members to keep talking to each other; dependent work must use current information | Actual communication gaps show a specific routing or checkpoint adjustment is needed |
| D10 | Let members choose relevant available skills and plugins within their assignment | Ody explicitly granted tool selection freedom | A tool is unavailable or a better supported option fits the task |
| D11 | Maintain one expanding private canvas with stable stage IDs and branches | Ody requested a whole plan whose canvas grows as work develops | The visual structure needs revision based on actual project work |

## Living canvas

[Open the living project plan](https://higgsfield.ai/canvas/92a49202-0f11-4fc0-8531-86fab2f535e8).

The saved board contains the three team roles, S1 to S8, dependency connections, Q1 to Q6, the proposed data structure and deferred directions. It grows through findings, decisions, experiments and results attached to stable stages. Board identifiers and the last verified source revision are in `CANVAS.json`; the update procedure is in `PLANNING_TEAM.md`.

This plan remains the current decision record, and the canvas presents it visually. Updates happen during active work rather than through automatic background synchronization.

## Open disagreements

None recorded in the current design cycle. The rules permit debate; no dispute between specialist agents has been simulated or claimed as actual work.

When a real material disagreement occurs, record the decision, affected task IDs, each position and evidence, resolution attempt, status and next action here. Use status open, resolved or escalated. Follow the decision brief in `PLANNING_TEAM.md` when asking Ody. Pause only tasks that depend on his answer and keep useful independent work moving.

## Parked work

| Work | Why deferred | Reopen trigger |
| --- | --- | --- |
| Face comparison and borrowed card checks | Extend beyond card presentation evidence | First milestone evaluated and Ody requests the next stage |
| Full app, live processing and dashboard | Do not resolve the first readability and card reading uncertainty | Offline baseline useful and delivery requirements known |
| Always running agents, timers and notification automation | Not implemented by this planning design; useful work is event based | Ody requests a specific schedule or event monitor |

## Current cycle and next action

Run: ROADMAP_2026_11_09. Lead: current main assistant. Starting revision: 6.

Current outcome: the lead documented the working milestone and open questions. The technical planner acknowledged its assignment, sent a useful partial finding, received the lead's response and returned a proposal. The lead accepted the planning deliverable and integrated its identifier branch, staged experiment, data records and evaluation cautions. The investigator stayed unassigned because sample access remains unconfirmed. No unresolved team disagreement arose.

Latest checks: private canvas created and its saved nodes and connections read back; all board writes inspected for rejection. Skill manifest validation and local record checks are recorded in `REPORT.md`, Entry 13. This cycle exercised actual lead and technical planner communication, but no samples, models or application code were tested. The data investigator did not run.

Next useful action: obtain a representative original clip or frames for P05 and the outstanding P06 answers. Use observed samples to refine S3, complete affected P04 checks and scope the first S5 experiment. Keep future stages provisional until their evidence exists.
