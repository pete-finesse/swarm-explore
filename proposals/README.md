# Shared context for the four proposals

Four candidate projects, one per file: `A-jpact-at-swarm-scale.md`, `B1-mind-viruses.md`, `B2-error-cascades.md` and `D-guard-down-for-peers.md`. Read this file first: it holds what all four share.

## The event

- **What:** Apart Swarm Alignment Hackathon, Nov 6–8 2026. Submissions close Sun Nov 8, 23:59 AoE.
- **Rules, judging and report format:** `../resources/sprint.md`.
- **Prior work:** allowed, but only weekend work is judged. Anything done before Friday must be declared as prior work.
- **Topic:** many-agent systems, so each project should be able to scale beyond a handful of agents.

## Constraints

- **Open models only.** Every project reads the J-space, which needs white-box access, so: open-weight models on a rented GPU (an 80 GB card costs roughly $2–3/h).
- **Self-funded.** Keep a running log of GPU hours and API spend.
- **Adaption credits:** $500 for hosted inference. They give no activations, so they only help black-box parts such as judges.
- **API keys.** Peter creates all accounts and keys and puts them in `.env`. Never commit `.env`, and never ask for key values.
- **Where to work.** Work only in `projects/<your project>/`. Clone third-party repos into its `repos/` subfolder and put downloaded data in its `data/` subfolder; git ignores both. Don't edit `proposals/` or `resources/`. Commit only your own folder (`git add projects/<your project>/`), never `git add -A`.

## J-space background and tools

- **Paper:** Gurnee, Sofroniew, … Lindsey (2026), https://transformer-circuits.pub/2026/workspace. Short version: https://www.anthropic.com/research/global-workspace.
- **Code:** https://github.com/anthropics/jacobian-lens. Start with `walkthrough.ipynb`.
- **Pre-fitted lenses** (no fitting needed): https://huggingface.co/neuronpedia/jacobian-lens. Read its README for the file format and the J++ variant. Interactive explorer: https://www.neuronpedia.org/jlens.
- **Reading lenses during generation** (nnsight + vLLM): https://nnsight.net/vllm/examples/jacobian-lens/.

## Known pitfalls

Read these before trusting any readout.

- **Lens target layer.** Many released lenses target the final layer, which distorts readouts: https://www.lesswrong.com/posts/Adb55vLqt33LEyBfz/j-lens-shouldn-t-target-the-final-layer-by-default.
- **Token-frequency bias.** Common tokens show up regardless of input. Z-score against a baseline: https://www.lesswrong.com/posts/Qe3jdphWCg9kny3e5/the-j-lens-offset-is-the-model-s-token-frequency-z-scoring.
- **Topics, not intentions.** The lens picks up whatever topic is in context: https://www.lesswrong.com/posts/GZCMmCHZiF8vhsczr/a-topic-detector-not-a-lie-detector-what-j-space-monitoring. Every comparison needs a control that contains the same words.
- **Logit-lens baseline.** In one careful negative result, the J-lens gave no advantage over the plain logit lens: https://github.com/viznu/jspace-obfuscation (see `RESULTS.md`). Always include the logit lens as a baseline.
- **Causal claims replicate weakly on open models:** https://www.lesswrong.com/posts/zFJ3ZdQwrTWE9jT5S/a-review-of-anthropic-s-global-workspace-paper.

## Wider reading

`../resources/lit-scan-jspace-swarms.md` is a literature scan of J-space and multi-agent work as of Nov 3 2026, written by another agent. Treat it as a map, not a source: many of its numbers and code links are unverified, so check anything you rely on against the original.
