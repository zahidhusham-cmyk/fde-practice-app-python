# Interviewer notes

**Spoilers.** Do not read this before a practice run. It is for self-review afterward, or for a friend acting as interviewer.

## The planted bug

**Where.** `backend/app/services/shipments.py`, in `ALLOWED_TRANSITIONS`. The `out_for_delivery` entry allows `delayed` and `cancelled`, but not `delivered`.

**What you'll see.** Dispatchers can open a shipment that is already out for delivery (try `HL-4412`, Brightleaf Market) and choose "delivered", but Save returns `400` with `Cannot transition from out_for_delivery to delivered`. Other legal transitions still work, for example booked → at_origin on `HL-4401`.

**How it is revealed.** `backend/tests/test_shipments.py` — `test_out_for_delivery_can_transition_to_delivered` — is intentionally failing. Manual check: open `HL-4412`, set status to delivered, and save. Other existing tests still pass; they cover list/detail shape, valid transitions, and clearly illegal ones such as booked → delivered.

**Good fix.** Add `"delivered"` to the allowed next statuses for `out_for_delivery`. Keep the rest of the state machine. Re-run `pytest` and confirm the previously failing test passes, then try the same change in the UI.

**Weaker fixes.** Changing the test to match the bug. Removing transition validation entirely so any status can be set. Hard-coding a special case for `HL-4412`. "Fixing" it only in the frontend by skipping the API.

## What good solutions look like

### Task 1 — Fix the delivery transition

A strong candidate runs the tests or reproduces the report in the UI, forms a hypothesis, reads the update path (`routers/shipments.py` → `ShipmentService.update_shipment` → `ALLOWED_TRANSITIONS`), and makes a small fix. They verify with the previously failing test and a quick UI check. They do not need to find it on the first guess, but they should work from evidence.

### Task 2 — Filter, sort, or a stats summary, end to end

A solid solution adds query params to `GET /api/shipments` (for example `q`, `status`, or `service_level`) and corresponding controls on the list page, or a small summary (counts by status) with an API and UI.

Look for:

- Filtering **before** pagination, so page totals reflect the filtered set. A common miss is paginating first, then filtering the page.
- Reusing the existing list response shape (`shipments` + `pagination`), or a clearly named companion endpoint for stats.
- An empty state when nothing matches.
- Case-insensitive search over a reasonable field set (id, customer, origin, destination).
- Status and service values that match the existing enums.

Debouncing a search box is a plus, not a requirement. Building only the API or only the UI is incomplete.

### Task 3 — Book a shipment

A solid solution adds `POST /api/shipments`, a form in the UI, Pydantic validation, and tests.

Look for:

- `POST`, not `PUT`. Creating a shipment is not idempotent; the server assigns the next id (`HL-44xx`). The response should be `201 Created` with the new shipment.
- Following the existing validation style: a Pydantic request model, `400` for business-rule failures with a `{ "detail": string }` body, and `422` for invalid types or enums is fine (that is FastAPI's default).
- Required fields such as customer, origin, destination, service level, promised date, weight, and pieces.
- `driver_id` optional, but rejected when it does not match a real driver (same idea as PATCH).
- A default status of `booked`, plus a created-at timestamp and an initial tracking event.
- A test for the happy path and at least one validation failure.
- UI that lets a dispatcher submit a shipment and then see it (navigate to the detail page, or refresh the list). New shipments should appear at the end of the default id order.

Weaker: no validation, inserting only in the frontend, using `PUT`, returning `200` without a new id, or a large form library that doesn't match the rest of the app.

### Task 4 — Draft a customer update (stretch)

A solid solution puts the drafter behind a small interface or injected function so it can later be swapped for an LLM, then ships a stub (for example, customer name, route, promised date, and the latest delay event).

Look for:

- An endpoint such as `POST /api/shipments/:id/customer-update` (or GET) that returns `{ "draft": string }`.
- A button on the detail page, ideally shown for delayed shipments, and a place to render the result.
- A test that mocks or stubs the drafter and does not call a real model.
- A 404 when the shipment does not exist, and a clear 400 if the shipment is not delayed (if that is the chosen rule).

Weaker: calling a real LLM from the test, hard-coding the stub in the route with no seam, or a large framework for a one-function feature.

## Rubric — working with an AI agent

Score the process, not just the diff.

| Signal | Strong | Weak |
| --- | --- | --- |
| Explore first | Reads the repo, runs the app or tests, and restates how pieces connect before generating a large change | Asks the agent to "do all the tasks" immediately, or spends the first stretch on a long chain of warm-up questions |
| Planning | Asks the agent to plan a small step, reviews and tweaks the plan, then implements | Jumps straight to a large implementation prompt |
| Prompting | Small, specific steps that point at existing files or patterns; reasoning said out loud before the prompt | One-shot prompts that try to finish the interview at once |
| Diff review | Reads each diff, edits or rejects mistakes, keeps unrelated refactors out | Accepts large diffs unread |
| Verification | Runs tests **and** a type or lint check (`pytest` plus `ruff`/`mypy`, or `tsc`) after changes | Assumes the agent got it right, or only notices type errors at the end |
| Review pass | Reviews their own diff first, then asks Cursor's review agent (or the chat agent) for a brief bugs/edge-cases pass, and acts on the findings | Declares done without reading the diff, ignores a finding, or burns minutes on a vague "review everything" prompt |
| HTTP semantics | Uses the right method and status (`POST` + `201` to create, `PATCH` to update) | Calls create a `PUT`, or ignores the existing error shape |
| Narration | Thinks out loud: hypothesis, tradeoff, next step | Long silences while the agent works |
| Handling mistakes | Pushes back when the agent is wrong, off-pattern, or too broad | Rubber-stamps bad or bloated changes |
| Time | Leaves a few minutes to summarize; can say what they'd do next | Still generating code when time is called |

A strong 45-minute session typically finishes tasks 1 and 2 cleanly, gets a solid start on 3, and may or may not reach 4. Finishing all four with sloppy process is a worse signal than finishing two carefully.
