# Archive: first planning round (Nov 4 2026)

On Nov 4, four candidate projects (A, B1, B2, D) each got a baseline plan. Peter then dropped B1 and D, and changed the goal: we now **scrutinise** two papers, J-PACT and Silent Dissent, rather than extending them. See `../../SCOPE.md`.

What's kept here, and why:

- `jpact-notes/`: project A's plan and explainer. They contain checked details about J-PACT's code, its cache and NARCBench, plus early weaknesses (the shared-private-text confound, no logit-lens baseline, a 31 vs 36 run-count mismatch, files missing from the cache).
- `silent-dissent-notes/`: project B2's plan and explainer. They contain checked details from the Silent Dissent repo and its supplement (the selection effect behind the 0.852, the log-rank logit-lens result, the free-debate E5 numbers).
- `proposals/`: the original proposals for A and B2, and the shared README of J-space tools and pitfalls. These proposals contain errors that the notes above correct.

**Treat all of this as unverified leads, not sources.** Each one proposes a project; those proposals are superseded. The B1 and D plans were not kept. Their last commits were `600af7c` (B1) and `4b321a2` (D), recoverable with `git branch <name> <sha>` until git garbage-collects them.
