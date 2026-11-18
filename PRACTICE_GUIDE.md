# Practice guide

Set a 45-minute timer and treat this like the real interview: screen shared, thinking out loud, Cursor open. You are not expected to finish every task. How you work matters more than how much you ship.

## Timed run

**0–5 min — Explore.** Skim the repo yourself before asking the agent to write code. Open the app, click through the list and a detail page, and run `make test` (or `pytest`). Note the main routes, how the UI talks to the API, and any existing tests or patterns you would reuse. Limit yourself to two or three warm-up questions. If you ask Cursor to explain the layout, combine related questions into one prompt (for example, "give me a breakdown of the app and where the shipment data comes from"), then say back what you understood and check a key file yourself.

**5–40 min — Tasks.** Work through [TASKS.md](./TASKS.md). Prompt one step at a time, review every diff, and run the app or tests after each change. Keep a few decisions for yourself: naming, structure, and what "done" means for the current task. If time is short, say what you would do next rather than rushing a messy finish.

**40–45 min — Wrap-up.** Stop adding features. Summarize what you changed, what you would test next, and any risks or follow-ups. Leave the project in a runnable state.

## How to prompt

Don't hand Cursor the whole interview in one prompt. A rhythm that works well:

1. Spend a few minutes reading the codebase yourself, talking out loud. You can ask Cursor to explain how the pieces connect, then restate it in your own words.
2. Ask Cursor to plan the next change before it implements anything. Review the plan, tweak it, and only then let it write code.
3. Give a specific next step and point at an existing file or pattern, for example: "Follow the validation in the shipment update route to validate this new payload."
4. Read the diff before you accept it. Say what you're checking and push back when it's wrong. Say your reasoning out loud before you type the prompt, for example "I think this transition is rejected because…"
5. Run tests and a type or lint check after each change (`pytest` plus `ruff check backend` / `mypy backend/app`, or `npx tsc --noEmit` in `client/`), so you're working from evidence.
6. For a bug, have it write or run a failing test before the fix when you can. For a feature, ask for tests as part of the plan, not only at the end.
7. If the agent stalls or overreaches, stop it, tighten the request, and continue.

What hurts a session: going silent while the agent works, accepting large diffs without reading them, asking a long string of warm-up questions before you start, or one-shotting every task and then debugging a mess.

## Suggested Cursor rules

A starter file is already in [`.cursor/rules/project.mdc`](./.cursor/rules/project.mdc). If you practice in a fresh clone, you can paste this into `.cursor/rules` or `.cursorrules`:

```
- Make small, focused diffs. Do not refactor unrelated code.
- Follow existing patterns, naming, and validation in this repo.
- Explain what you changed and why.
- After a change, say how to verify it (test or manual check).
```

## Before you call a task done

Review your own diff first. Then do a short final pass with Cursor's review agent (or ask the chat agent to review the change). Ask it to look for bugs and edge cases only — keep the prompt brief so you don't burn interview time. You stay the reviewer: accept or reject its notes, and act on what it finds. Either fix the issue or say "I'll note that and come back." Then run the tests and a typecheck once more.

## Self-review checklist

Use this after the timer, before you read [INTERVIEWER_NOTES.md](./INTERVIEWER_NOTES.md).

- Did I look at the codebase (and run the app or tests) before generating a large change?
- Did I keep warm-up questions to two or three, and say back what I understood?
- Did I prompt in small steps instead of one-shotting the whole task list?
- Did I say my reasoning out loud before prompting, and narrate tradeoffs as I went?
- Did I read each diff and catch at least one thing I would have rejected or edited?
- Did I run tests and a type or lint check (`pytest`, `ruff`/`mypy`, or `tsc`) after changes, not only at the end?
- Did I act on the review agent's findings, either by fixing them or explicitly deferring them?
- When the agent was wrong or too broad, did I push back rather than accept it?
- Did I use the right HTTP semantics (for example, POST and `201` to create a shipment)?
- If I ran out of time, could I clearly say what I would do next?
