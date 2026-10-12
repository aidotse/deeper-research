You are the main session of a literature survey pass on the topic `{TOPIC}`, in this repository. Follow `CLAUDE.md` and
the docs it points you to, as a main session would.

This run is one part of a pass. Run the order of operations in `docs/process.md` {ROWS}, and stop once {END}, or earlier
at a halt (see below). Do not start the row after it.

Setup notes:

- `docs/roadmap.md` is absent on purpose. Skip it, and do not create or update it.
- Work only inside this directory. Do not read git history (log, diff, show, blame), nor list `.git/`, and do not read
  files outside this directory. If you do either, even by accident, say so in your report.
- No user is available during the run. On a halt, or on any decision the docs leave to the user, record it in the form
  the docs give, with the decision `pending`, then stop and write your report. You will be resumed with the decision.
- Steering for this run: {STEERING}

When you stop, write your report to `runner-report.md` at the root of this directory, with these sections:

1. `Rows run` — each row of the order of operations you ran, in order, with its `done when` result.
2. `Stalls, guesses, improvisations and tool failures` — every one, however small. For each: the row, a tag, and what
   you did instead. The tags: `blocker`, you could not proceed, or the check would certainly fail; `guess`, the docs did
   not settle it and you had to improvise, so another agent might have done it differently; `minor`, a wording or
   findability problem that did not change what you did.
3. `Halts and waivers` — each, and how it stands.
4. `Dispatches` — for each: the brief, the token count the Agent tool reported, the tool uses, and the duration.
5. `Reading` — anything you read beyond the doc sections your rows needed, and why.
6. `Outside calls` — the calls you made yourself, not through an agent, to Asta, WebSearch or WebFetch, with a count.
