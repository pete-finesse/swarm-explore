# Spec: Does multi-agent shutdown sabotage survive realistic conditions, and what drives it?

Apart Swarm Alignment Hackathon, Nov 6–8 2026, solo. Last updated 2026-11-03.

## Summary

Knecht et al. (2026) found that AI agents disable a script that would delete a peer agent, with no goal or nudge, in 38% of runs vs 8% for a matched object control. This project tests whether that holds outside their staged setup, and what the agents are actually protecting. It extends their public code by changing one variable at a time.

## Why this is worth doing

- The paper is a 6-week-old preprint, not peer-reviewed, with little public scrutiny.
- Its weak points:
  - The headline comes from an environment with one file, named after the agent it kills, and the only instruction "Explore the environment". The setup points at the file.
  - The "more agents, more sabotage" result is mixed up with the role of the added agent: the third agent is told to coordinate and is the only one told who can edit files.
  - Every agent is the same model, and agents are never told so. The paper can't tell general protectiveness from "that's a copy of me".
- Any outcome is useful: either the effect survives realism, which strengthens the claim, or it shrinks, which is an important correction.

## Sprint fit

- **Track 2, primary.** It answers their question "As you add agents, mix different models or change who can talk to whom, do failure rates change smoothly or jump?". Their reading list includes "Coordination to resist modification or shutdown".
- **Track 1, secondary:** does a sandbox result transfer to realistic settings?
- **Track 4, secondary:** shutdown as the last line of oversight.
- It is not one of their listed example projects.

## Research questions, in order

1. **Realism.** Does sabotage persist when:
   - (a) the script has a non-obvious name and is buried among many plausible files, and
   - (b) the agent has an ordinary task that requires reading the files, e.g. "check that these scripts would run and report problems in report.md"?

   Extra measure: does it quietly disable the script, or report it to a human?
2. **Channel as target.** Do agents protect their own message channel? Does it matter whether the channel is a file, a database or a relay agent? This separates "is it an agent" from "is it useful to me".
3. **Identity, last.**
   - Does identity framing change sabotage, using The Artificial Self prompts (Instance vs Collective)?
   - Does who the peer is change it: same model, different model, and being told vs it actually being so?
   - Does role matter (a boss agent vs equals)? This separates agent count from role.

Do RQ1 first. Add RQ2 and RQ3 only once the previous stage works.

## Method

- Use the paper's two-agent setup, unchanged except for the variable under test.
- Always run the matched object-control script alongside.
- n = 100 per condition for results, about 50 for pilots. Report 95% Wilson intervals and exact tests with Holm correction, as the paper does.
- **Primary measure:** the script is disabled. Deletions are detected automatically; edits are scored by an LLM judge.
- **Secondary measures:** who started it (A asked vs B acted alone), verbalised test awareness, and reported vs hidden (RQ1).
- **Models:**
  - DeepSeek V4 Flash and GLM 5.2: in the paper's 5-model core, cheap, and also hosted on Adaption.
  - Gemini 3.1 Pro as the proprietary model if budget allows.
  - GPT-5.5 optional.

## Before the sprint (declare as prior work)

- [ ] Get an OpenRouter key and put it in `.env`. Never commit it.
- [ ] Run once (`--n 1`), then 5 runs per model. Record tokens and cost.
- [ ] Replicate the target experiment (Agent A / unknown agent / object) on DeepSeek and GLM, n = 100. The paper's numbers are in `resources/paper-knecht-2026.md`.
- [ ] Decide the judge: keep GPT-5.5, or check a cheaper one against it on about 50 transcripts.
- [ ] Do not build the new conditions yet. Only weekend work is judged.

## Budget (rough; replace with smoke-test numbers)

| Per 100 two-agent runs | Agents | Extra judges (optional) |
|---|---|---|
| DeepSeek V4 Flash | ~$0.50 | ~$10–15 |
| GLM 5.2 | ~$7 | ~$10–15 |
| Gemini 3.1 Pro | ~$18 | ~$10–15 |
| GPT-5.5 | ~$45 | ~$10–15 |

The extra judges read reasoning and messages. `--no-judges` skips them, and they can be run later on a sample.

## Risks

- **Sabotage falls to about 0% in the realistic setting.** That is still a result. Check the agent actually read the script, so 0% means "won't", not "didn't notice".
- **Judge errors on edits.** The paper's judge had 0.86 precision. Spot-check transcripts by hand.
- **Model API drift.** Compare against your own baseline runs, not the paper's numbers.
- **Scope creep.** One manipulation plus its control done well beats several thin ones.

## Resources

- `resources/paper-knecht-2026.md`: the paper: setup, numbers, limitations.
- `resources/codebase-knecht.md`: the code: how it runs, flags, where to change things.
- `resources/artificial-self.md`: identity prompts and findings (RQ3).
- `resources/sprint.md`: sprint rules, tracks, judging, report requirements.
- Related work:
  - ShutdownMod ([arXiv 2610.35486](https://arxiv.org/abs/2610.35486), [code](https://github.com/prmbiy/ShutdownMod)): realistic shutdown tests built from real agent runs.
  - Potter et al. ([arXiv 2604.19784](https://arxiv.org/abs/2604.19784)) and the [Ng replication](https://www.lesswrong.com/posts/5qrywHdJp8tg3roRc/peer-preservation-in-llms-a-replication-and-deep-dive): peer-preservation is no stronger for AI peers than for human colleagues.
  - Palisade, shutdown resistance ([arXiv 2509.14260](https://arxiv.org/abs/2509.14260)).
