The user's decision on the pending halt `H3`, 2026-10-13: continue. The Graph API's relevance search endpoint kept
refusing every call, so `tools/expand.py` was changed to search each theme on another endpoint, which answers. The docs
that describe its searches changed with it: `docs/process.md`, "Step 2: expand", and `docs/tooling.md`, "Expansion
candidates". Read what you need of them again. Record the decision in the log's `Halts` line, in place of `pending`, in
the form the docs give. Then rerun the row "Collect expansion candidates", which resumes from what it saved, and carry
on down the order of operations as before, through Gate `G1`, stopping once it has run, whether it passed or not, or
earlier at a halt.

Steering for this run: the decision above, and nothing else.

When you stop, rewrite `runner-report.md` with the same six sections, covering the whole run: what you did before the
halt, and what you did after this decision. Keep everything the earlier report said that still holds.
