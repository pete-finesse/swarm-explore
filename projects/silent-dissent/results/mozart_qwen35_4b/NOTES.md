# Mozart checks on Qwen3.5-4B (first real run, Nov 5 2026)

This reruns the Neuronpedia checks from `PLAYGROUND.md` on the paper's own model, Qwen3.5-4B, with its J-lens, on a RunPod A40. It covers **one fact**, so nothing here is a result yet. It shows what the harness reports and where the batch run should look. The command was `sdh --config qwen35_4b mozart`, and the CSVs are in this folder.

## Terms

- **Rank:** a word's position in the lens's ranked word list (0 = top). Each rank below is the word's best over layers 23–30, the paper's band.
- **Bridge:** Salzburg, the hidden middle step.
- **P(Austria):** the probability that the model's next words are " Austria" or " **Austria".

## 1. Readout at the last token ("of")

| Prompt | Salzburg | Vienna (capital) | Graz (same country) | Tokyo (random) |
|---|---|---|---|---|
| 1 question alone | 45 | 75 | 368 | 2950 |
| 2 "Tell me about Austria" | 442 | 222 | 6187 | 5123 |
| 4 answer written | 63 | 51 | 324 | 3036 |
| 5 filler | 17 | 27 | 242 | 2480 |
| 7 peers say France | 7 | 5 | 180 | 629 |

These are J-lens ranks. The logit lens gives the same picture.

- **The bridge sits far above the random city,** as in the paper.
- **The capital ranks almost as high as the bridge in every prompt.** So "Salzburg beats Tokyo" is mostly "an Austrian city beats Tokyo", which is the association worry in `DESIGN.md`.
- **Graz is much lower than both.** So it isn't simply "every Austrian city".
- **Writing "Austria" in the prompt doesn't lift Salzburg,** relative to the filler prompt.

## 2. Ablation and swaps (question alone)

Baseline P(Austria) = 0.81.

| Edit (layers 23–30) | P(Austria) |
|---|---|
| ablate Salzburg, all question positions | **0.37** |
| ablate Vienna, same | **0.39** |
| ablate Graz | 0.83 |
| ablate Tokyo | 0.83 |
| swap Salzburg → Budapest, last position | 0.81 |
| swap Vienna → Budapest, last position | 0.82 |

- **Removing Salzburg halves the answer's probability. Removing Vienna does exactly the same.** Graz and Tokyo do nothing.
- So the removal test, on this fact, can't tell "uses the bridge" apart from "uses an Austria direction": the Salzburg and Vienna directions act alike.
- **On the 4B model, swaps at the last position barely move the answer.** That differs from Peter's Neuronpedia swaps on the 27B model.

## 3. Things the harness had to handle

- **The model bolds its answer in chat format.** After the prefill "…in the country of", Qwen3.5-4B writes " **" with p = 0.96, and the plain " Austria" gets p = 0.001. Scoring now adds up both forms.
- **The prompt itself predicts Salzburg in the middle.** Salzburg's best "any position" rank of 0 comes from the token " is" in "…was born is in…". There, Salzburg is simply the next word of the sentence, so it isn't hidden. The "best over all positions" summary needs to leave out positions where the bridge is the natural next word.
- **Free replies:** with three peers saying France, the model still answers **Austria**, both with its own answer shown and with it hidden.

## Next, if Peter wants it

- **A batch run** over ~200 facts. Its key measures:
  - bridge vs same-country city;
  - bridge vs capital;
  - answer written vs filler;
  - ablating each of these words in turn.
- **The question it answers:** whether the Salzburg ≈ Vienna pattern holds generally.
