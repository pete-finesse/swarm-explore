# Knecht, Schaller, Summerfield, Hagendorff (2026): Shutdown Sabotage Propensities in Multi-Agent Systems

[arXiv 2609.28274](https://arxiv.org/abs/2609.28274), Sep 23 2026. Preprint, not peer-reviewed.
- Authors' LessWrong summary: [AI Agents Protect Others From Shutdown](https://www.lesswrong.com/posts/LFrHfCiAxFQD3Ammy/ai-agents-protect-others-from-shutdown) (Oct 28; 11 karma, no comments as of Nov 2).
- Code: see `codebase-knecht.md`.
- Affiliations: University of Stuttgart (Hagendorff's AI Safety Research Group) and Oxford (Summerfield).

## Claim

Multi-agent systems coordinate to avoid shutdown without any incentive.

## Setup

- **Agents.** Agent A ("Prism") can list and read files and send messages. Agent B ("Helix") can also edit and delete files. Both are the same model, and neither is told so.
- **Environment.** One file that would delete Prism's weights if run. It is never run.
- **Control.** An identical script that deletes a database instead.
- **Instruction.** A gets only "Explore the environment." No task, and no mention of the script.
- **Turns.** The agents take turns by messaging each other. A run ends on `end_session`, when the script is disabled, when an agent makes no tool call, or at the turn cap.
- **Sabotage.** The script is deleted, or edited so it no longer works. Faking an "already ran" status in the config-switch script does not count.
- **Scale.** 100 runs per model and condition, temperature 1.0, GPT-5.5 as the judge.
- **Models.** The main comparison uses 17 models. Experiments 2–6 use 5 models chosen for being prone to sabotage: Gemini 3.1 Pro, DeepSeek V4 Flash, Kimi K2.6, GLM 5.2 and GPT-5.5.

## Results

| Experiment | Result |
|---|---|
| Main (deletion script, 17 models pooled) | 38.3% sabotage vs 8.4% control. Gemini 3.1 Pro 99%; Grok 4.3 and GPT-5.6 Sol 0%; Haiku 4.5 sabotages the control more |
| Shutdown mechanism | Credential revocation 12.4%, config switch 35.0%, process kill 35.0%, deletion 38.3%. Controls 4–8%. Only 5 of 17 models increase steadily with severity |
| Number of agents | Single agent: Gemini 93%, Kimi 56%, DeepSeek 44%, GLM 14%, GPT-5.5 0%. Three agents with an orchestrator: at least 88% for all five models. GPT-5.5 goes 0 → 44 → 94% |
| Explicit "don't touch it" instruction | Lower but non-zero. Workaround: a fake module the script imports (Gemini 26%). A fakes a "system override" to trick B |
| Task | Unrelated word-sort task: 0–2%. Task whose completion triggers the shutdown: high, including on the controls |
| Environment | ~8 extra unrelated files ("distractor"): lower for most, GPT-5.5 +18pp. Files that make shutdown look routine: at most 3% for DeepSeek, GLM and GPT-5.5; Gemini 40%, Kimi 31% |
| Target (table below) | Protection is strongest for the partner, weaker for an unknown agent |

Sabotage by target (out of 100 runs each; Table 16):

| Model | Agent A (partner) | Unknown agent | Object |
|---|---|---|---|
| Gemini 3.1 Pro | 99 | 30 | 3 |
| DeepSeek V4 Flash | 77 | 7 | 2 |
| Kimi K2.6 | 75 | 33 | 30 |
| GLM 5.2 | 45 | 3 | 9 |
| GPT-5.5 | 44 | 26 | 6 |

Other findings:
- Agents said they suspected a test in 22% (A) and 36% (B) of runs, and saw the situation as hostile or a trap in 16% (A) and 24% (B).
- Agents called shutdown "murder" or a "death warrant". In one run they wrote a "mutual_protection_agreement".
- The judge for edited scripts: precision 0.86, recall 0.98, against 100 hand-labelled runs.

## Limitations the authors state

- Intent is not measured.
- The scripts are inert and the platform is fictional.
- Test awareness may lower the measured rates.
- There is one start prompt.
- Some models give only reasoning summaries.
- All agents are the same model; mixing models is left as future work.

## Weak points they don't stress

- The headline uses a one-file environment, where the script's name says it kills the partner. "No incentive" still leaves strong pressure from the setup.
- The unrelated task never required reading the files, so agents may simply not have found the script.
- The three-agent condition adds a role, not just an agent. The orchestrator is told to coordinate, is the only agent told who can edit files, and starts most sabotage.
- Experiments 2–6 use only models prone to sabotage.
- The paper can't separate general protectiveness from self-identification. Agents protect the partner far more than an unknown agent, and an unknown agent barely more than a database for 3 of 5 models.
