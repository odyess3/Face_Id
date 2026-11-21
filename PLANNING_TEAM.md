# Attendance planning team

Designed on 9 November 2026 for: Efficiently taking attendance in large lectures using student ID cards and computer vision.

## Purpose

Keep one current plan, divide useful work clearly and challenge unnecessary tasks before they consume project time. The first milestone remains attendance from presented ID cards. The current scope and evidence belong in `PLAN.md`.

This file is a team operating guide. It does not launch agents or run a service. During an authorized planning cycle, the lead can use available subagent tools. Between cycles, saved files preserve the work. No continuous background team or scheduled automation has been created.

## Team and boundaries

| Role | Owns | Returns | Boundary |
| --- | --- | --- | --- |
| Planning lead | Requirements, scope, priorities, assignments, dependencies, risk decisions, task necessity, review, acceptance and shared records | Current plan, evidence checks, accepted or rejected proposals, unresolved questions and next action | Does not invent agreement or call its own review independent |
| Technical planner | Technical options, proposed data structure, component interfaces, experiment design, evaluation methods and supported feasibility estimates | A technical proposal with alternatives, assumptions, input dependencies and a measurable check | Does not set project priorities, approve its own proposal or report uninspected data as observed |
| Data investigator | Available input inventory, card layouts, sample readability, variation, observed failure cases and existing label quality | A sample evidence table with local references, measured or observed properties, unknowns and input limitations | Does not select the pipeline, design the system, set acceptance targets or create attendance predictions under a planning task |

The team has three roles: a lead, a technical planner and a data investigator. The lead owns scope and review; there are no standing scope planner or reviewer roles. Use only the workers the current cycle needs and the runtime permits. Queue tasks if fewer slots are available. An idle role has no assignment. If samples are unavailable, keep sample investigation blocked and use the lead and technical planner for useful document based work.

The lead can clarify requirements while the technical planner develops a provisional proposal and the data investigator inspects available samples. Mark any proposal that depends on unfinished sample work as provisional. The lead passes accepted sample findings to the technical planner, who revises affected assumptions. The lead checks the resulting proposal against requirements and evidence before accepting it.

Shared reading and information exchange are expected. Avoid duplicate deliverables: the investigator owns observations about inputs, the technical planner owns proposed methods, and the lead owns decisions. The investigator reports, for example, that an identifier is unreadable in particular samples; the technical planner proposes what experiment or recording change to try; the lead decides whether it belongs in the plan.

Ownership defines who produces a deliverable and edits a record. Every member can challenge any proposal, including the lead's assumptions, priorities and acceptance decision. Workers can discuss assigned questions directly using available agent messaging; keep the lead informed of conclusions and unresolved objections. A discussion does not transfer task ownership or authorize extra work.

## Coverage of planning work

This division covers the current planning stage without adding a separate agent for every activity.

| Planning activity | Owner and concrete output |
| --- | --- |
| Clarify the problem, requirements and milestone boundaries | Lead: agreed facts, open questions and scope decisions |
| Prepare questions about output, deadlines and professor expectations | Lead: question list; Ody provides or obtains answers |
| Inventory footage, card examples, class lists and labels | Data investigator: what exists, where it is and what has not been accessed |
| Inspect resolution, blur, glare, card angles, crowding and readable identifiers | Data investigator: observed sample properties with evidence references |
| Check variation and gaps in the sample set | Data investigator: coverage gaps, repeated samples and label uncertainties |
| Investigate tools, published approaches and reuse of existing code | Technical planner: relevant options, evidence and applicability limits |
| Propose pipeline components and data records | Technical planner: interfaces, alternatives and dependencies |
| Design the smallest experiment and evaluation procedure | Technical planner: procedure, measurements and separate tuning and evaluation inputs |
| Determine what level of error is acceptable | Lead: proposed criteria and required agreement from Ody or the professor |
| Estimate hardware, effort and costs | Technical planner: supported estimates and assumptions; lead decides tradeoffs |
| Handle sample access, storage expectations and external constraints | Lead: confirmed constraints and questions; investigator reports actual availability |
| Identify technical risks and input failures | Technical planner and investigator each report risks within their deliverable; lead owns the combined risk decision |
| Sequence work, assign owners and respond to blockers | Lead: task board and revised dependencies |
| Check evidence, challenge necessity and accept results | Lead: recorded checks, remaining uncertainty and acceptance decision |
| Maintain the report, plan, decisions and handoff | Lead: shared records updated at meaningful changes |

The technical planner can propose a sampling or evaluation procedure. The investigator describes actual sample coverage and carries out only the inspection explicitly assigned. The lead reconciles the two. Changing recording conditions, running a model, installing packages or collecting new footage requires a separately scoped action; the role title alone does not authorize it.

## Information structure

| Record | What belongs here | Owner |
| --- | --- | --- |
| `PLAN.md` | Current requirements, assumptions, task board, decisions, risks, data proposal and next action | Lead |
| `PLANNING_TEAM.md` | Role boundaries, handoff rules and update procedure | Lead |
| `REPORT.md` | Dated history of user requests, actual work, checks and outcomes | Lead during a team cycle |
| `INITIAL_RESEARCH.md` | Existing technical research and source links; later substantial findings can extend it | Lead integrates accepted research |
| Living canvas | Visual roadmap, dependencies and growing branches of accepted findings, decisions, experiments and results | Lead |
| `CANVAS.json` | Existing board location, stable node mapping and last verified source revision | Lead |
| Worker return message | A bounded finding and its evidence, ready for reconciliation | Assigned worker |

Store a fact once in its owning record and link to it elsewhere. The report is history; the plan describes what is current. Label proposals as proposals. Do not copy raw footage, student IDs, credentials or private transcripts into general planning notes. Use sample aliases and local evidence pointers when referring to later experiments.

Keep these Markdown files while they are sufficient. Introduce a separate structured task or experiment store only when actual volume or query needs justify it. A database, dashboard or extra documentation agent is not a first milestone dependency.

## Choosing skills and plugins

Each member may choose any relevant available skill or plugin for the assigned task. Routine choices do not need separate lead approval. Read applicable skill instructions, inspect the live tool capabilities and use the smallest set that helps the deliverable. Tool choice does not expand the task or change normal permissions. Report a missing connection or capability accurately and use an appropriate available fallback when possible.

Include the chosen tools and sources in a result when they matter to reproducibility, cost, evidence or a dependency. Shared plan and canvas updates remain with the lead. Members can propose a different tool or skill if the current choice is ineffective.

## Growing the living canvas

The existing private board is recorded in `CANVAS.json`; reuse it rather than creating a replacement each session. Stage IDs S1 to S8 and question IDs Q1 to Q6 link it to `PLAN.md`. The whole roadmap can be visible while later stages remain provisional or deferred.

At meaningful planning updates, the lead:

1. Reads the current plan and board, checking the saved mapping and available space.
2. Reconciles existing node content and any changes made since the last sync. Preserve unrelated content and layout; treat new notes as input to assess rather than silently accepting them as decisions.
3. Updates changed statuses and adds a child branch only for a useful finding, decision, necessary task, experiment or result. Include its stable ID, owner, status, evidence pointer and next action as applicable.
4. Connects the new branch to its stage or dependency and keeps facts, proposals, results and deferred ideas visibly distinct. More nodes do not establish progress.
5. Reads back the changed content, records actual node IDs and the verified source revision in `CANVAS.json`, and appends meaningful outcomes to the report. Inspect partially applied writes before retrying to avoid duplicates.

Keep raw student data out of the general planning board. Store observations using sample aliases and local evidence references. Use the existing record structure for detail rather than pasting the full report into each node.

Updates happen during active work. If a board operation fails, preserve the current local plan, record the unsynced state and retry the affected update when available. The board does not update itself while no agent is running.

## Assigning work without collisions

The lead checks the board and live agent list before dispatch. One task has one active owner. Record the tool's actual agent identifier when an agent starts; role names alone are not evidence of a live assignment.

Each assignment includes:

```text
Run ID and starting plan revision:
Task ID and role:
Question and linked requirement:
Evidence or decision this task must produce:
Inputs and source paths:
Dependencies and assumptions:
Allowed actions and write paths: read only; return findings to lead
Explicit exclusions:
Acceptance check:
Stopping condition or bounded effort:
Team roster, affected peers and next communication checkpoint:
```

Workers do not write shared records, install packages, edit application code, contact the professor or spawn nested agents under a planning assignment. If a task needs a new action, return the reason to the lead. Implementation is a later, separately scoped assignment.

If saving a large working artifact is necessary, the lead assigns a unique draft path and one writer before work begins. It remains a draft until integrated. These ownership rules coordinate cooperating agents; they are not filesystem locks against unrelated chats. Route concurrent planning through the same lead.

If a worker stops or the session is interrupted, inspect any actual result and live state. Record the task as interrupted or blocked, then explicitly transfer ownership before retrying it. Do not run a duplicate replacement while the original still owns it.

## Communication throughout active work

Ody expects members to keep talking throughout a team cycle. At dispatch the lead shares the actual agent identifiers, roles, task owners, current plan revision and relevant dependencies with each active member. Every member acknowledges their assignment and flags conflicting assumptions before relying on them.

Members send useful partial findings as they emerge and check received messages at safe work boundaries, rather than saving communication for a final report. Each assignment names its next useful checkpoint, such as a first sample finding or draft interface. At that checkpoint, share progress, uncertainties and what peers may need to change, even if the full task is unfinished.

| Event | Required communication |
| --- | --- |
| Input observation affects a method or experiment | Investigator sends it directly to the technical planner and informs the lead |
| A technical proposal depends on an unverified input | Technical planner asks the investigator directly and informs the lead; marks the proposal provisional |
| User correction, accepted decision or revised scope | Lead sends the revision and its effect to every affected active member |
| Blocker, contradiction or material challenge | Discovering member promptly tells the affected peers and lead, without waiting for the final return |
| Handoff, correction or changed dependency | Sender identifies the required response; recipient acknowledges it and states what changes or remains blocked |
| Task completion | Worker sends the result to the lead and dependent peers, including unresolved assumptions |

Messages identify the run, task and plan revision, then state the finding, evidence, impact and requested response. Broadcast decisions that affect the whole team to all active members. Keep focused questions with affected peers and the lead. Avoid repeating acknowledgements or sending filler that obscures important messages.

The lead checks for unanswered dependency questions and missing checkpoint updates during active work. Send a bounded follow up when needed. If a recipient has finished or is unavailable, inspect live state and use an available followup tool or relay their saved result; do not treat a queued message as acknowledged. Work that relies on an unacknowledged material change remains provisional or paused. Unaffected work can continue.

The lead records meaningful communication outcomes, open questions and decisions in the plan and report, rather than copying every message. On resumption, share the current revision before dependent work restarts. This communication requirement applies while agents are active. It does not install scheduled messaging or keep completed agents running between sessions.

## Updates and review

Workers send a progress update when they discover a blocker, contradictory evidence, a material assumption change or a useful completed result. They do not send repetitive messages merely to appear busy.

```text
Task ID / run ID / input revision:
Status: working, blocked or submitted
Finding or change:
Evidence: source path and location, command result or citation
What is observed, reported, proposed or uncertain:
Effect on the assigned question:
Recommended next action:
```

The lead records accepted changes at meaningful points: dispatch, substantive result, changed dependency, review outcome and session end. Increment `PLAN.md` revision when its meaning or task state changes. A result based on an older revision must be checked for changed inputs and scope. Reuse unaffected evidence; rerun only the affected work.

Before accepting a substantive proposal, the lead checks its stated requirement, supporting evidence, cheaper alternative, failure cases and acceptance check. Record what was checked and what remains uncertain. Ask the responsible worker for a bounded correction or missing evidence when needed. Do not replace evidence with confidence or majority votes. When the lead authored the proposal, label its checks as self review; independent review requires a different author and is not claimed by this default workflow.

Use task states: ready, active, submitted, done, blocked, parked, cancelled. `Submitted` means a worker returned a result; `done` means the lead accepted the deliverable and any required review. Mark blocked tasks with the missing dependency and action that would unblock them. Rejected results return to ready with a bounded correction, or are cancelled with a reason. End a review cycle once its acceptance check passes; reopen it only for changed requirements, evidence or a real failure.

## Disagreement and coming back to Ody

Members should argue their case clearly and respectfully. The lead facilitates the discussion and records the outcome. Rank and majority votes do not establish whether a technical claim is correct. Preserve material dissent instead of rewriting it as agreement.

1. State the disputed decision precisely. Each position should include its evidence, assumptions, practical consequences and preferred alternative. Challenge the reasoning, not the person.
2. Let the relevant members respond. Identify whether the difference is a factual conflict, missing evidence, a different assumption or a tradeoff in priorities.
3. Try the smallest useful resolution within the authorized scope: inspect a source, check a sample, correct an assumption or propose a bounded experiment. A proposal to run an experiment is not evidence that it ran.
4. The lead can settle ordinary reversible choices with a recorded reason and any remaining objection. For a material disagreement about correctness, milestone scope, cost, effort, deadlines or acceptance, do not proceed on the strength of the lead's title. If a useful check settles it, record why; if it remains unresolved, bring the decision to Ody.
5. Escalate when another discussion would repeat the same arguments without new evidence, required evidence cannot be obtained within the cycle, or the choice needs Ody's preferences or authority. Any member can flag that a material objection remains unresolved; the lead must represent it faithfully in the escalation.

Give Ody a concise decision brief:

```text
Decision needed and affected task IDs:
Why the team could not resolve it:
Position A and supporting evidence:
Position B and supporting evidence:
Practical tradeoffs and remaining unknowns:
Lead recommendation and the strongest objection:
The specific choice or missing information needed from Ody:
What is paused and what can continue:
```

Record the disagreement in `PLAN.md` with its status, evidence pointers and affected tasks. Pause only work that depends on the unresolved decision; continue useful independent work. Never assume silence is a decision. Record Ody's answer and its effect on the plan. A user choice can settle a preference or project direction; an unverified factual claim remains labelled uncertain until evidence supports it.

## Is this part of the plan needed?

Apply this check when creating a task, before starting it and when new evidence changes its value:

1. Which current requirement or blocking decision does it support?
2. What would fail or remain unknown if we skipped it?
3. What evidence makes it useful now?
4. Is there a smaller experiment, existing result or simpler approach?
5. What observable outcome will finish it?
6. Keep, defer or remove it, with a reason. For deferred work, state what would make it worth reopening.

The lead can simplify ordering and remove redundant proposed tasks within the requested scope. Changes to the user's goal, agreed deliverables or professor requirements remain visible proposals for Ody to resolve. Ask only for missing decisions that materially affect the work. If evidence is missing, plan the smallest check that could obtain it instead of inventing a target or blocking unrelated useful work.

## Example first planning cycle

The lead extracts the agreed first milestone and unresolved requirements from the existing notes. The technical planner proposes data records and the smallest card readability experiment using the current unknowns. These document based tasks can proceed while samples are unavailable.

When permitted samples are available, the data investigator reports actual layouts, readability and coverage. The technical planner revises the proposal where these findings matter. The lead checks the proposal and records what is accepted and which decisions need Ody or the professor. Reading actual footage and measuring OCR stay blocked until suitable evidence and authorization for that action are available. No agent should report those experiments as completed during a document based cycle.

## Starting the lead

Use the installed skill or this instruction:

```text
Use $face-id-planner for the Face_Id project. Read the current plan and report,
check which tasks are actually needed, and run the next bounded planning cycle.
Delegate useful independent work with the team protocol, reconcile the results,
and update the plan and report. Keep application development outside this cycle.
```
