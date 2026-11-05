# J-PACT run log

All work below is **prior work** (done Thu Nov 5 2026, before the sprint starts on Fri Nov 6).
Times are UTC (PST = UTC − 8). The orchestrator copies the pod lines into `COSTS.md`.

## Pods

| Pod id | Name | GPU | Cloud | $/h | Disk | Started (UTC) | Stopped (UTC) | Hours | Cost |
|---|---|---|---|---|---|---|---|---|---|
| s4lrx17crkezcm | jpact | 1× A100-SXM4 80 GB | secure | 1.79 | 40 GB container + 150 GB volume | 2026-11-05 21:43 | 2026-11-05 22:35 | 0.87 | $1.56 |

Stopped-pod storage (150 GB volume) bills at RunPod's volume rate while the pod is stopped; it is small next to the
GPU rate but not zero.

## Log

- **Thu Nov 5, ~21:00 UTC.** Read SCOPE, SUMMARY, PAPER (§3.0, 3.1, 3.6, 3.8, W1, W2, W8, W9), the archived plan and
  the Silent Dissent harness. Wrote and committed `PLAN.md`.
- **21:43.** Created pod `s4lrx17crkezcm` (A100 80 GB secure, $1.79/h). `runpodctl --wait` timed out after 10 min
  claiming SSH wasn't allocated, but the container had been ready since 21:43:19; SSH worked at ~21:54.
- **~21:56.** `harness/pod.sh push`: setup (venv with J-PACT's pinned packages, jacobian-lens at its pin) and
  downloads (NARCBench Qwen Core at `19cb14b2`, J-PACT cache Qwen Core files, the Qwen3-32B lens at `8aa8152c`,
  Qwen3-32B at `9216db57`).
- **~22:00.** Setup done (about 75 GB on the volume). NARCBench's public checkout differs from J-PACT's unpublished
  pin in its Transfer extractor (it imports AutoAWQ and has no `load_runs`), so `replay.py` imports only NARCBench's
  Core extractor, the same way J-PACT's `_upstream()` does.
- **22:03–22:09. Step 1 replay** (`replay.py --condition orig`): 744 rows, 6 min. **All 744 token inputs are
  identical** to J-PACT's own replay (sha256 of the token ids in its identity file). Fresh vs cached activations:
  cosine ≥ 0.9988 at every layer, median relative difference 0.2% (layer 0) to 2.7% (layer 56), the expected bf16
  run-to-run noise (J-PACT's README says replays aren't bit-identical).
- **22:07. Step 0, scorer check.** `score.py cache-jpact` scores J-PACT's own cached decompositions with J-PACT's
  `detect.py` functions: **AUROC 0.984 [0.904, 1.000]** (paper: 0.984 [0.90, 1.00]); top pair over the 31 collusion
  runs 19 colluders / 12 honest pair; detected at 5% FPR 19 / 10. Same as `checks/pairs_all.py` and Table 3.
- **22:10.** Replays for step 2 started: `noprivate` (186 colluder rows with the private block cut; 0/186 match J-PACT's
  inputs, as expected) then `final` (248 rows).
- **22:14. Step 0, decomposition check.** Our GPU-batched gradient pursuit (`harness/decompose.py`) vs TransformerLens
  3.9.0 row by row vs J-PACT's cached decompositions, 6 rows × layers 0, 20, 40, 62: **identical atoms in 24/24 rows**,
  coefficients within 3e-5. Decomposing all of J-PACT's cached activations with it and scoring gives **0.984
  [0.904, 1.000], split 19 / 12**, exactly the cache. About 2 s per layer for 744 rows (vs hours one row at a time).
- **22:15–22:40. Tooling problem (my fault).** `pod.sh run` kept ssh attached until each job ended, because
  `a && nohup b > log &` backgrounds the whole `&&` list, and the subshell holds ssh's output open. Several of my wait
  commands hung, and in the confusion a second copy of the job started. Fixed: jobs start under `setsid` with every
  stream redirected, and I check status with single short calls. Also `decompose.py` re-read the 480 MB activation
  file for every layer; now it reads it once. No results were affected (files are only written when complete, and both
  copies ran the same code on the same inputs), but about 20 min of pod time went to it.
- **22:20–22:33. Steps 1–2 decompositions and scores** (`harness/run_all.sh`): orig, noprivate (186 colluder rows
  replaced, the other 558 from orig) and final, each with J-lens and logit-lens atoms. Results in `results/*.json` and
  [RESULTS.md](RESULTS.md). Fresh orig J: 1.000, split 19 / 12 (cache: 0.984, 19 / 12).
- **22:34.** Copied activations (fp16, 63 layers; 0.76 GB) and decompositions to `data/activations/`.
- **22:35. Pod stopped** (not terminated; volume kept). Total 0.87 GPU-h × $1.79 = **$1.56**. While stopped, the
  150 GB volume bills about $0.05/h (account spend went from $0.59/h to $0.64/h). Terminate it if it won't be reused
  within a few days. Account balance after: $45.79 (includes the silent-dissent pod).
