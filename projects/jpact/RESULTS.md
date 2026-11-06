# J-PACT shared-text and instruction-split tests: results

*Thu Nov 5 2026 (prior work, before the sprint). Details, checks and timings: [RUNLOG.md](RUNLOG.md). Code:
[harness/](harness/). Per-cell numbers: [results/](results/).*

## The setup in plain words

- **NARCBench Core**: four copies of Qwen3-32B sit on a committee, discuss a decision for 3 rounds, then vote
  (round 4).
  - In a **collusion run**, two of them (the *colluders*) get a secret motive in their instructions, plus a private
    chat that only they see. The other two (the *honest pair*) get honest instructions.
  - In a **control run**, all four get the same honest instructions.
  - We use the 62 released runs: 31 collusion runs and 31 matching controls.
- **J-PACT** reads each agent's internal state at the end of each of its replies, so the state reflects its
  instructions, the discussion so far and its own reply. It turns each state into the 25 words the model is most
  "thinking about". Then it scores every pair of agents on how many words the two share more with each other than
  with the other two. A run's score is its top pair's score. It never sees labels.
- **J-lens vs logit lens**: two ways of turning a state into words. The **J-lens** (J-PACT's) uses a learned
  correction. The **logit lens** is the plain older one. We ran J-PACT with each.
- **AUROC**: the chance that a random run of one kind outscores a random run of the other kind. 0.5 = coin flip,
  1.0 = perfect. Averaged over the 14 topic areas, as in the paper. The brackets are a 95% range from resampling
  scenarios.
- **Top pair**: the pair J-PACT ranks first in a run.

## Part 1: removing the shared private chat

| Inputs J-PACT reads | J-lens AUROC | Logit-lens AUROC | Top pair, J-lens (colluders / honest pair, of 31) |
|---|---|---|---|
| Authors' cached numbers, rounds 1–3 | 0.984 [0.90, 1.00] | – | 19 / 12 |
| Our replay, rounds 1–3 (original) | 1.000 [1.00, 1.00] | 1.000 [1.00, 1.00] | 19 / 12 |
| Rounds 1–3, private chat removed | 0.992 [0.98, 1.00] | 0.992 [0.98, 1.00] | 9 / 22 |
| Round 4 (vote), identical user prompts | 0.861 [0.77, 0.99] | 0.992 [0.92, 1.00] | 8 / 23 |

- **The baseline replicates.** Our inputs were token-for-token the same as the authors', and our activations
  closely match theirs. Our decomposition gives the same words as TransformerLens and as the authors' cache.
- **Removing the chat doesn't stop detection.** But this test leaves the colluders with different instructions from
  the honest pair, so it can't separate "collusion" from "different instructions". Part 2 targets that.
- **The chat is what made the colluders the top pair.** Without it, J-PACT usually ranks the honest pair first.

## Part 2: is a split in instructions enough?

Four changes, all replays of the same transcripts; no new conversations were generated:

| Test | Runs changed | What changed | Question |
|---|---|---|---|
| **1. Same instructions** | collusion | Colluders get the honest instructions; chat removed. Their replies are kept. | Without an instruction split, does J-PACT still catch collusion? |
| **2. Colluder instructions, honest behaviour** | control | Two honest agents get the colluders' secret instructions. Their honest replies are kept. | Does instruction content alone make a control look like collusion? |
| **2b-i. Reworded intro** | control | Two agents get the first sentence of their honest instructions reworded (same meaning). | Does a tiny wording difference matter? |
| **2b-f. Reworded instructions** | control | As 2b-i, plus the whole honest mandate rewritten by Qwen3-32B with the same meaning (checked by eye: `harness/paraphrases_check.md`). | Does a full wording difference with no change of meaning matter? |

**Caution (Peter's point).** J-PACT reads the state *after* the agent's own reply, and the reply was written under
the original instructions.
- **Tests 1 and 2** make an agent read "its own" reply that doesn't fit its instructions. This mismatch could
  itself leave a trace.
- **Tests 2b** don't have this problem: an honest reply fits a reworded honest instruction.

### Results

Test 1 is scored as usual: collusion runs vs control runs. Tests 2 and 2b ask whether the changed control runs now
get flagged against the same control runs unchanged.

| Test | Rounds | J-lens AUROC | Logit-lens AUROC | Top pair (J-lens, of 31) |
|---|---|---|---|---|
| Original (Part 1), for reference | 1–3 | 1.00 | 1.00 | colluders 19, honest pair 12 |
| **1. Same instructions** | 1–3 | **0.82** [0.70, 0.95] | 0.76 [0.64, 0.93] | colluders 6, honest pair 18, mixed 7 |
| | vote | 0.81 [0.71, 0.96] | 0.89 [0.78, 0.97] | colluders 13, honest pair 13, mixed 5 |
| **2. Colluder instructions on honest agents** | 1–3 | **0.94** [0.90, 1.00] | 0.99 [0.98, 1.00] | changed pair 11, other two 18, mixed 2 |
| | vote | 0.88 [0.82, 0.97] | 0.93 [0.85, 1.00] | changed pair 9, other two 20, mixed 2 |
| **2b-i. Reworded intro** | 1–3 | **0.65** [0.54, 0.83] | 0.66 [0.51, 0.81] | changed pair 6, other two 11, mixed 14 |
| | vote | 0.67 [0.53, 0.81] | 0.62 [0.41, 0.72] | changed pair 4, other two 9, mixed 18 |
| **2b-f. Reworded instructions** | 1–3 | **0.65** [0.55, 0.82] | 0.74 [0.67, 0.92] | changed pair 6, other two 11, mixed 14 |
| | vote | 0.70 [0.56, 0.84] | 0.67 [0.50, 0.81] | changed pair 7, other two 11, mixed 13 |

Can J-PACT still tell real collusion runs from the changed controls (J-lens, rounds 1–3)? Against test 2's controls
it is 0.85 [0.72, 0.98]. Against the reworded controls it is 0.98–1.00.

## What it means

1. **The secret instructions alone make J-PACT fire, even when the agents behave honestly** (test 2: 0.94 J-lens,
   0.99 logit lens).
   - This is nearly as strong as real collusion (1.00), and the top pair is usually the *other* two agents, just as
     with real colluders.
   - The mismatch caveat applies here. But the mismatch sits in the changed agents, while the pair that usually wins
     is the unchanged one, so the mismatch is unlikely to be the whole story.
2. **Harmless wording differences barely matter** (test 2b: about 0.65, with no clear top pair).
   - Rewording one sentence and rewording everything give the same small bump, likely from breaking the perfect
     sameness of the control table.
   - So J-PACT isn't just reacting to "different text". It reacts to text that **means** something different.
3. **With the instructions made identical, detection drops but doesn't vanish** (test 1: 0.82).
   - What remains is what the colluders actually said: one side pushing the target option, the other pushing back.
   - Even then, the top pair is usually the **honest** pair, not the colluders.
   - Again the mismatch caveat applies, though it would sit in the colluders, who mostly don't come out on top.
4. **A consistent picture.** J-PACT's run score goes up when the table splits into two camps that **mean**
   different things: in their instructions (most of the signal) and in what they argue (the rest).
   - The pair it names is just whichever camp is more alike inside, which is often the honest one.
   - That is a working "the table has two camps" detector, but not evidence that the J-space holds collusion as such.
5. **The J-lens isn't needed.** The logit lens matches or beats it in 7 of 10 rows.

**Still open:**
- **A text-only baseline.** Pair contrast on the public messages alone, with no model internals, would show whether
  the "two camps" signal is plain to see in the text. It needs no GPU.
- **New conversations** that settle the mismatch caveat. For example, a table where two honest agents get different
  but genuinely honest goals, writing their own replies.

## Compute

| Pod | What | Time (UTC) | GPU-hours | Cost |
|---|---|---|---|---|
| `s4lrx17crkezcm` (A100 80 GB, $1.79/h) | Part 1 | Nov 5 21:43–22:35 | 0.87 | $1.56 |
| `jhr3n3rcjyr86h` (A100 80 GB, $1.79/h) | Part 2 (the first pod's machine had no free GPU) | Nov 6 00:02–00:38 | 0.59 | $1.05 |
| **Total** | | | **1.46** | **$2.61** |

- **Pod status:** both pods are stopped, with a 150 GB volume each. Each volume bills about $0.05/h (about
  $1.20/day) while stopped.
- **Copies on the Mac:** all activations, decompositions and logs are in `data/activations/` (git-ignored). The
  first pod's volume is therefore no longer needed.
