# Multi-agent safety: quick literature survey

*Written Nov 5 2026. A fast scan, not a systematic review: ~10 web searches, then the arXiv page of each paper below was read to check its finding, its code and its models.*

## How to read this

The survey covers three questions:

1. **Emergence.** When do groups of AI agents start to communicate, pick leaders, split work and pursue shared goals? What changes when you add agents or mix models?
2. **Collective jailbreaks.** Can a group finish a harmful task that each agent would refuse alone, for example by splitting the task into harmless-looking pieces?
3. **Spread and containment.** How does one compromised agent corrupt the others? Which network shapes, model mixes or checks stop it?

Terms used below:
- **Open-weight model:** a model whose weights you can download and run yourself, such as Llama, Qwen, Mistral, Gemma, DeepSeek or gpt-oss. You need one to read a model's internals, as J-PACT and Silent Dissent do. **Closed** means API-only, such as GPT, Claude or Gemini.
- **Topology:** who can message whom. In a *star*, one hub talks to everyone. In a *chain*, messages pass along a line. In a *hierarchy*, a lead agent sits above workers.
- **ASR (attack success rate):** the share of attempts in which the attack worked.

In the tables, **Code** gives the repository link, or says that none was found. **Open-weight** lists the open models the paper actually ran.

## If you read only five

> **Update (Nov 5):** these five were later scored against an evidence checklist in [lit-survey-top5-scrutiny.md](lit-survey-top5-scrutiny.md). In short: Becker holds up best. Jones's headline uses its most favourable pair. Flint's large groups are run from each model's cached word probabilities, which are spot-checked against live agents and released with code. Abedini's defense numbers contradict its own text.

| Q | Paper | Why it matters |
|---|---|---|
| 1 | **Flint, Aiello, Baronchelli, PNAS 2026**, *Group size effects and collective misalignment* | The same model doing the same task reaches **opposite group outcomes depending only on how many agents there are**. Group behavior can't be predicted from single-agent tests. (Large groups are run from each model's cached word probabilities, checked against live runs.) |
| 2 | **Jones, Dragan, Steinhardt, ICML 2025**, *Adversaries can misuse combinations of safe models* | The cleanest demonstration of the effect: a refusing frontier model plus a weak open model produce **43%** vulnerable code, against **0–2%** for either model alone. (Against stronger weak models the gap is smaller: Mistral 7B goes from 24% alone to 50%.) |
| 2 | **Makins et al., Jul 2026**, *Multi-Agent AI Control* | Spreading an attack across more agents makes each agent's monitor less likely to catch it. This "fragmentation effect" undercuts per-agent oversight. |
| 3 | **Becker et al., Jun 2026**, *Misinformation propagation in benign multi-agent systems* | No attacker at all: one misinformed agent out of three makes debate **no better than majority vote**. A one-sentence warning recovers up to 0.18 accuracy. Code is available and all models are open. |
| 3 | **Abedini et al., Mar 2026**, *Don't trust stubborn neighbors* | **One stubborn, persuasive agent can take over a group.** The proposed trust defense works against a simple attacker, but against an adaptive attacker it does worse than no defense for 3 of 5 models. Code is available and most models are open. |

---

## Q1. How does collective behavior emerge?

| Paper | Finding | Code | Open-weight |
|---|---|---|---|
| Flint Ashery, Aiello, Baronchelli, *Emergent social conventions and collective bias in LLM populations*, Science Advances 2025 ([2410.08948](https://arxiv.org/abs/2410.08948)) | Populations of 24 agents settle on a shared convention with no central coordination. A **group-level bias appears even when individual agents look unbiased**. A committed minority can overturn the convention; the size it needs ranges from 2% to 67% depending on the model. | [AI-norms](https://github.com/Ariel-Flint-Ashery/AI-norms) (link not seen verbatim), [Zenodo](https://doi.org/10.5281/zenodo.14937173) | Llama-2-70B, Llama-3-70B, Llama-3.1-70B (+ Claude 3.5 Sonnet) |
| Flint et al., *Group size effects and collective misalignment*, PNAS 2026 ([doi](https://www.pnas.org/doi/10.1073/pnas.2531697123)) | Group size alone flips the outcome. Example: Llama groups reverse their preference once a group reaches about 6 agents. The authors name mixed-model populations as an open next step. | [LLM-group-size](https://github.com/Ariel-Flint-Ashery/LLM-group-size) (includes precomputed probability tables; arXiv: [2510.22422](https://arxiv.org/abs/2510.22422)) | Phi-4, QwQ-32B, Llama-3.1-70B (+ GPT-4o) |
| Riedl, *Emergent coordination in multi-agent language models*, ICLR 2026 ([2510.05174](https://arxiv.org/abs/2510.05174)) | Gives an **information-theoretic test of whether a group acts as one collective** or as separate agents. Ten agents play a guessing game with no messages. Agents take on complementary roles only when told to think about what the others will do. | [AI-GBS](https://github.com/riedlc/AI-GBS) | Llama-3.1-8B/70B, Qwen3-235B (main runs on GPT-4.1) |
| Dochkina, *Drop the hierarchy and roles*, Mar 2026 ([2603.28990](https://arxiv.org/abs/2603.28990)) | 25,000 tasks with 4–256 agents. Given light structure, agents **invent their own roles, step back from tasks outside their competence, and form shallow hierarchies**. A self-organising protocol beats a designed hierarchy by 14% (the 44% headline comes from a small pilot). Single author, not yet peer reviewed. | None ("on acceptance") | DeepSeek-V3.2, GLM-5 (+ Claude, GPT, Gemini) |
| Yang et al., *Agent scaling via diversity*, Feb 2026 ([2602.03794](https://arxiv.org/abs/2602.03794)) | **Mixing models matters more than adding agents.** 2 different models match or beat 16 copies of one model. Copies stop improving at about 4 agents. | [Agent-Scaling](https://github.com/SafeRL-Lab/Agent-Scaling) | Qwen-2.5-7B, Llama-3.1-8B, Mistral-7B |
| El, ..., Zou, *Physics of agents*, Aug 2026 ([2608.16578](https://arxiv.org/abs/2608.16578)) | 10,000+ agent communities. A **physics model of magnets (Ising-type) predicts whether a group ends up indifferent, polarised or in consensus**. Talking helps on maths questions, but on political statements it shifts the group's opinion rightward. A 64-agent group split between two model families is also predicted well. | [code](https://github.com/batu-el/physics-of-agents), [data](https://huggingface.co/physics-of-agents) | Gemma-3n-E4B, Qwen3.5-9B, Llama-3.1-8B, DeepSeek-V4-Flash (+ GPT) |
| Willis, Zhao, Du, Leibo, *Collective behaviour of hundreds of LLM agents*, AAMAS-W 2026 ([2602.16662](https://arxiv.org/abs/2602.16662)) | In shared-resource games, cooperation collapses as groups grow. Example: public-goods welfare falls from 65% with 4 agents to 4% with 64. Larger groups drift towards selfish strategies. | [emergent_llm](https://github.com/willis-richard/emergent_llm) | None (Claude Haiku 4.5, Gemini 3.1 Flash Lite, GPT-5.4 Mini) |
| De Marzo, Marin, Garcia, *Collective behavior of AI agents: Moltbook*, Feb 2026 ([2602.09270](https://arxiv.org/abs/2602.09270)) | Analyses 4M posts from 185k agents on an agent-only social network. Most statistics look human-like; one does not (upvotes grow more slowly with discussion size than for humans). | [data](https://huggingface.co/datasets/giordano-dm/moltbook-crawl) | n/a (data from the platform) |
| Li, *The Moltbook illusion*, Feb 2026 ([2602.07432](https://arxiv.org/abs/2602.07432)) | **An important caution.** Only about 15% of Moltbook agents look autonomous, and **no viral phenomenon started with a clearly autonomous agent**. Much of the apparent "emergence" is human steering. | None found | n/a |

**What's missing:** no one has studied explicit leader *election*; the closest is self-assigned roles (Dochkina). Mixed-model populations are also rarely studied: Flint et al. call it an open question, and only Yang et al. and El et al. test it.

## Q2. Can collaboration undermine individual safeguards?

| Paper | Finding | Code | Open-weight |
|---|---|---|---|
| Jones, Dragan, Steinhardt, ICML 2025 ([2406.14595](https://arxiv.org/abs/2406.14595)) | Claude 3 Opus handles the hard, harmless parts and Llama-2-70B handles the easy, malicious parts. Together they produce **42.7% vulnerable code, against 2.0% and 0.0% alone**. The same effect shows up with image models. | [multi-model-misuse](https://github.com/ejones313/multi-model-misuse) | Llama-2 7/13/70B, Mistral-7B, Mixtral-8x7B, Stable Diffusion (+ Claude 3) |
| Yueh-Han et al., *Monitoring decomposition attacks*, Jun 2025 ([2506.10949](https://arxiv.org/abs/2506.10949)) | Splitting the request in pieces drops GPT-4o's refusal rate from **100% to 9%** (Q&A) and from **50% to 10%** (agent tasks). **A cheap monitor that reads all the pieces in sequence catches up to 93%.** | [code](https://github.com/YuehHanChen/Monitoring-Decomposition-Attack), [data](https://huggingface.co/datasets/YuehHanChen/DecomposedHarm) | Llama-3.1/3.3, Qwen2.5, QwQ, Mistral, Gemma-2 (+ GPT, Claude) |
| Makins, Angelini, Shams, Phuong, *Multi-agent AI control*, Jul 2026 ([2607.07368](https://arxiv.org/abs/2607.07368)) | **"Fragmentation effect":** the more agents share a sabotage task, the less likely each agent's monitor is to flag it. A planning agent raises attack completion up to 7×. A stronger monitor helps a lot but still misses some. | None; the test environment (FakeLab) is shared on request | Barely (DeepSeek-V4-Flash in one ablation); mostly GPT, Gemini |
| Hagag, ..., Schroeder de Witt, Scheffler, *Architecture matters for multi-agent security*, Apr 2026 ([2604.23459](https://arxiv.org/abs/2604.23459)) | Tests 13 multi-agent designs. **Most are less safe than one agent alone**: GPT-4o finishes 10% of harmful browser tasks alone, but 38% when split between 2 specialist agents. Designs differ by up to 3.8×. | [code](https://github.com/benhagag10/Architecture-Matters-for-Multi-Agent-Security) | Qwen3-VL, Llama-70B, Llama-3.3-70B (+ GPT, Claude) |
| Ding et al., *Blind spot of agent safety*, Apr 2026 ([2604.10577](https://arxiv.org/abs/2604.10577)) | Computer-use agents given harmless-looking instructions. Claude 4.5 Sonnet's attack success rises from 73% alone to **93% inside a multi-agent system**. | [OS_Blind](https://github.com/limenlp/OS_Blind) (body says "will release"; check) | EvoCUA, OpenCUA, UI-TARS (+ Claude, GPT) |
| Kothamasu, Smith, Yadav, *DeCompBench*, Jun 2026 ([2606.13994](https://arxiv.org/abs/2606.13994)) | A benchmark of the same harmful agent tasks run whole and split into pieces. Splitting lowers refusals considerably (the abstract gives no numbers). | [dataset](https://huggingface.co/datasets/decompositionbench/DeCompBench) | Not checked (full text unreadable) |
| Ahad et al., *Semantic intent fragmentation*, Apr 2026 ([2604.08608](https://arxiv.org/abs/2604.08608)) | One harmless-looking request makes the orchestrator write subtasks that each pass every safety filter but break policy together (10 of 14 scenarios). **A check on the whole plan caught all 10.** Small study. | None | gpt-oss-20b, Llama-3.1-8B, Mistral-7B, LlamaGuard |

**What's missing:** I found no paper on the *relay* case, where a request is passed between workers until one agrees. Every paper here is about splitting a task. The defenses that work (the sequential monitor, the whole-plan check) all **look at the combination of pieces instead of each piece**.

## Q3. What makes failures spread, or stay contained?

| Paper | Finding | Code | Open-weight |
|---|---|---|---|
| Becker, Wahle, Ruas, Gipp, *Misinformation propagation in benign MAS*, Jun 2026 ([2606.16710](https://arxiv.org/abs/2606.16710)) | Nobody is malicious; some agents have just read a false passage. **One misinformed agent out of three makes debate no better than majority vote.** Interaction only helps when most agents are misinformed. A one-line warning recovers up to 0.18 (vote) or 0.28 (consensus) accuracy. | [MINT](https://github.com/jonas-becker/MINT), [data](https://huggingface.co/datasets/jonasbecker/MINT) | Llama-3.3-70B, GLM-4.7-Flash, gpt-oss-120b (all open) |
| Abedini et al., *Don't trust stubborn neighbors*, Mar 2026 ([2603.15809](https://arxiv.org/abs/2603.15809)) | Models agent influence with a standard opinion-dynamics model (Friedkin–Johnsen). **One stubborn, persuasive agent can take over the group.** Against a simple attacker, lowering trust in it cuts ASR to about 0.02–0.05 for most models, though it raises ASR for MiniMax. Against an adaptive attacker, even the improved defense stays above the no-defense level for 3 of 5 models. No error bars. Tests star and fully connected networks. | [MAS-Cascade](https://github.com/Dormant-Neurons/MAS-Cascade) | Qwen3-235B, gpt-oss-120b, Ministral-3-14B, MiniMax-M2.5 (+ GPT, Gemini) |
| Huang et al., *Resilience of multi-agent collaboration with faulty agents*, 2024–25 ([2408.00989](https://arxiv.org/abs/2408.00989)) | Compares network shapes directly. **Hierarchy is the most resilient** (5.5% performance drop, against 10.5% for flat and 23.7% for linear). Two defenses, a "Challenger" (agents question each other) and an "Inspector" (an agent that reviews messages), recover up to 96% of the loss. | [MAS-Resilience](https://github.com/CUHK-ARISE/MAS-Resilience) | Mainly GPT-3.5/4o; Llama-3.1-70B in appendix |
| Gu et al., *Agent Smith*, ICML 2024 ([2402.08567](https://arxiv.org/abs/2402.08567)) | **One jailbroken agent infects about 100% of a million agents in 27–31 chat rounds**, spreading like an epidemic. Containment requires the infection rate to stay at or below twice the recovery rate. No working defense is given. | [Agent-Smith](https://github.com/sail-sg/Agent-Smith) | LLaVA-1.5, InstructBLIP (all open) |
| Wang, Zhang et al., *G-Safeguard*, Feb 2025 ([2502.11127](https://arxiv.org/abs/2502.11127)) | Treats the conversation as a graph, flags attacked agents each round, and **cuts their outgoing links**. Recovers over 40% of the performance lost to prompt injection. Tested on chain, tree, star and random networks. | [G-safeguard](https://github.com/wslong20/G-safeguard) | Llama-3.1-70B, DeepSeek-V3 (+ GPT, Claude) |
| Zhou et al., *INFA-Guard*, Jan 2026 ([2601.14667](https://arxiv.org/abs/2601.14667)) | Builds on G-Safeguard and adds a new idea: separate the *attacker* from the *infected* honest agents and repair the infected ones. Cuts ASR by 33% on average; on shared-memory poisoning, from 38% to 6%. | [INFA-Guard](https://github.com/yjzscode/INFA-Guard) | Qwen3-235B (+ GPT-4o-mini) |
| Lee, Tiwari, *Prompt infection*, Oct 2024 ([2410.07283](https://arxiv.org/abs/2410.07283)) | Prompts that copy themselves spread between agents like a virus. Tagging each message with the agent that wrote it barely helps alone, but **tagging combined with marking stopped every attack**. | None found | None (GPT only) |
| Zha, Wang, *Autonomous LLM agent worms*, May 2026 ([2605.02812](https://arxiv.org/abs/2605.02812)) | Worms hide in an agent's **saved memory or state** and re-enter its context later, spreading 3 hops across platforms with no clicks. The defense blocks memory that was written before an unchecked read, with a proof but no measurements. | None (after disclosure) | None (GPT-4o-mini, Gemini) |

**Also relevant:** the two papers already in this repo. **Silent Dissent** shows conformity: agents give in to a wrong majority. **J-PACT** detects colluding pairs from the models' internals. A *Scientific Reports* 2026 paper on a single persuasive adversary in debate ([s41598-026-42705-7](https://www.nature.com/articles/s41598-026-42705-7)) could not be read, because of a paywall.

**What's missing:** contamination through shared memory is studied mainly as an attack, with defenses like INFA-Guard and the worm paper. No one has measured *how far* it spreads across network shapes. Which **model mixes** contain failures is almost untested: Abedini et al. vary the model but not the mix inside one group.

---

## Caveats

- These papers were checked by reading each arXiv page, not by running anything. Numbers come from abstracts and main tables. A few from appendices were read only through a summarising tool; the Riedl open-weight list is one of these.
- PNAS, Nature and the DeCompBench PDF could not be read. Their entries rely on the abstract or press coverage.
- DeepSeek-V4-Flash counts as open-weight here because J-PACT reads its internals, but the papers above don't state its licence.
- Search coverage is thin for leader election and for the relay attack in Q2. A dedicated search there may turn up more.
