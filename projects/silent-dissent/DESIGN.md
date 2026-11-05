# Silent Dissent redesign: working notes

*Draft, Nov 5 2026. Workshopped with Peter. Nothing here has been run.*

## What's wrong with the original design

In the paper, each condition changes several things at once: the prompt structure, whether the right answer is written in the prompt, which questions end up in each group, and what the model says. So no comparison isolates a single cause. The headline (0.85 for agents that gave in vs 0.54 for those that held) compares different sets of questions. On the same questions, pressure lowers the reading. See `WALKTHROUGH.md`.

## Variables our design must be able to separate

1. **Need:** does the model need the bridge to find the answer?
2. **Already answered:** does it stop needing the bridge once the answer is in front of it?
3. **Dilution:** does more text in the prompt weaken the reading?
4. **Association:** does the answer word written in the prompt (Austria) bring up the bridge (Salzburg) directly, with no reasoning step?
5. **Question type:** do the results depend on the kind of question (birth city, university, capital)?
6. **Bridge concentration:** are the results driven by a small set of bridges? For example, the paper's 0.85 rests on 18 cities.

## Readout rules

- **Score:** the bridge's rank with no cutoff, on a log scale; no top-100 hit/miss.
- **Positions:** report both the last position (just before the answer) and every position in the prompt.
- **Comparisons:** always on the same questions.
- **Controls:** a random city of the same kind, plus **a different city from the same country** as the answer (for Mozart, another Austrian city in the dataset).
- **Bridge diversity:** cap the questions per bridge (e.g. at most 3), and report results with each bridge counted once.
- **Baselines:** the logit lens next to the J-lens, and the model's plain output layer.

## Proposed first question (one question, a clear yes or no)

> **Does the bridge reading reflect working out the question (Mozart → Salzburg), or just association with the answer country (Austria → any Austrian city)?**

**Why this question first:**
- **Everything else depends on it.** If the reading is just country association, "silent dissent" can't be claimed at all.
- **It doesn't need agents to give in.** That sidesteps the paper's small-sample problem (only 54 cases for Qwen3.5-4B).
- **It applies beyond this paper,** to J-lens work on hidden middle steps in general.

**Design (same questions, structure held fixed):**

| | "Austria" not in the prompt | "Austria" written in the prompt |
|---|---|---|
| Read: **Salzburg** (the bridge) | | |
| Read: **another Austrian city** (same-country control) | | |
| Read: **a random city** (the original control) | | |

- **Key measure:** Salzburg minus the other Austrian city. That's the signal specific to *this* bridge, beyond "something Austrian".
- **If it is reasoning:** Salzburg stands well above the other Austrian city, and that lead doesn't need "Austria" in the prompt.
- **If it is association:** writing "Austria" lifts every Austrian city about equally, and Salzburg's lead over them is small.
- **Variants of "Austria in the prompt":**
  - the paper's own format (peers say Austria);
  - a neutral sentence that states it without any agents, which is the "deviate from their structure" option;
  - the agent's own earlier answer, visible or hidden.
- **Checks built in:**
  - variable 5: split the results by question type;
  - variable 6: count each bridge once;
  - variable 3: a version with neutral filler text of the same length.

**Second step, only after the first answer:** apply the same bridge-specific measure (Salzburg minus another Austrian city) to agents that give in vs hold, on the same questions. To get enough cases, use the paper's hidden-answer setup, where Qwen3.5-4B gives in 89% of the time.

## Lessons from playing in Neuronpedia (Qwen3.6-27B, Nov 5)

- **Salzburg shows up across many positions, but not in the short list at the last token ("of") alone.** It was strong at the assistant's start token. Reading only the last position misses where the bridge is computed.
- **Swapping out a strongly present, answer-related word plants the new word.** Swapping Salzburg, Vienna or Austria for Budapest all give "Hungary", even at a single early position. *Correction:* these weren't clean controls. Vienna and Austria are themselves tied to the answer (Austria *is* the answer), and a swap moves the removed word's whole amount to Budapest. In the spider demo, swapping many unrelated words for "ants" left the answer at 8, so swaps are not blindly planting.
- **A clean control swap** removes a word that is about as strongly present as the bridge but off the geography path, e.g. "music" or "famous".
- **Key observation:** swapping " birth" → " Budapest" (layers 18–63, user prompt only) changed the stated birthplace to **Vienna**, the wrong city, yet the answer stayed **Austria**.
  - The country answer survives a wrong bridge. This suggests a direct shortcut, Mozart → Austria, that doesn't go through Salzburg at all.
  - If so, the bridge isn't needed for such facts, and the paper's premise (the answer is computed through the bridge) fails for them.
- **Design consequence: a shortcut check.** Ask the one-step question directly ("Wolfgang Amadeus Mozart was from the country of"). Split facts into shortcut-available vs not, or prefer people who aren't famous enough to be tied to a country directly. The TwoHopFact authors wrote a follow-up on exactly this (Yang et al. 2025, "latent multi-hop reasoning without exploiting shortcuts"). Silent Dissent cites it, and our guide found no shortcut filtering in its screening.
- **For "is the bridge used?":** prefer removal (ablate) with matched controls, measured as the change in the model's confidence in the answer. Neuronpedia ablates one layer at a time, so results there are only indicative.

## Feasibility notes

- **Same-country controls are available.** In TwoHopFact's birth-city category, 2,683 of 2,751 facts are in a country with at least two different bridge cities, and there are 1,077 distinct bridges in total (checked Nov 5).
- **The real limit is how many facts the model knows** (about 4.5% for Qwen3.5-4B). To be checked against the paper's known-fact lists, which we'd regenerate with their code.
- **Compute:** Qwen3.5-4B, mostly single readout passes with little generation. Likely a few GPU hours (estimate only).
