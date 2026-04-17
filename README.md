# ExProf-Bench-Results

**ExProf-Bench** is a clinically informed benchmark for measuring executive control failures in large language models, grounded in validated executive-function constructs without claiming diagnostic or mechanistic equivalence to humans.It was developed for the **Kaggle × Google DeepMind AGI Hackathon 2026 — Track: Executive Functions** and evaluates whether a model can coordinate cognition under competing constraints, not merely retrieve knowledge. [file:81][file:55]

This repository is the **complete technical appendix and public results companion** to the hackathon submission. It includes the benchmark rationale, the six-task architecture, the Executive Profile Index (EPI), consolidated findings, and the main empirical result: a **jagged frontier** in executive control, where larger models do not reliably dominate smaller ones across dissociable executive-function dimensions. [file:81][file:55]

---

## Why this benchmark exists

Most current LLM benchmarks reward retrieval, pattern completion, or broad problem-solving competence. ExProf-Bench instead asks a narrower and more important question: **can a model maintain, inhibit, switch, monitor, and coordinate task sets under pressure and interference?** [file:55]

The benchmark is motivated by converging evidence that LLMs can show strong memory or fluent language behavior while failing in tasks that require **fluid executive control**, especially under rule shifts, dual-task load, and interference. The theoretical framing in this repository draws directly on the executive-function literature and on recent LLM studies documenting memory-control dissociations and perseverative failures. [file:55]

---

## Core contribution

ExProf-Bench contributes three things:

- A **6-task executive-function benchmark** grounded in clinical neuropsychology rather than generic reasoning prompts. [file:81][file:55]
- A **fully deterministic scoring pipeline** with 100 Python evaluators and no LLM-as-judge component. [file:81][file:55]
- A global impairment metric, the **Executive Profile Index (EPI)**, that turns dissociable failures into a single interpretable score while preserving task-level diagnostic meaning. [file:81][file:55]

The central empirical finding is that frontier performance is **not smooth**. Several tasks saturate for strong models, but **T5 TrailBench** sharply re-separates the field and reveals a discontinuous executive-control ceiling. [file:81]

---

## Benchmark summary

| Property | Value |
|---|---|
| Track | Kaggle × Google DeepMind AGI Hackathon 2026, Executive Functions [file:55] |
| Tasks | 6 dissociable executive-function tasks [file:81][file:55] |
| Total items | 150 items [file:81][file:55] |
| Evaluators | 100 deterministic Python evaluators [file:81][file:55] |
| Judging | No LLM judge, no embedding similarity, no probabilistic scoring [file:55] |
| Models evaluated | 33 models [file:81] |
| Output focus | Pass rate by task, cross-task profile, global EPI [file:81][file:55] |

---

## Theoretical framework

ExProf-Bench is structured around the **Unity-and-Diversity** model of executive functions proposed by **Miyake et al. (2000)**, which distinguishes related but separable executive processes such as inhibition, shifting, and updating. The benchmark uses that framework to justify six tasks that are cognitively related but empirically dissociable. [file:55]

Two clinical anchors guide the construct design and interpretation:

- **BADS** (*Behavioural Assessment of the Dysexecutive Syndrome*) provides the structural basis for T1, T2, T3, and T4. [file:81][file:55]
- **BRIEF-2A** provides the normative adult reference used to orient interpretation of aggregate executive impairment. Its adult norm sample is **n = 1,637**. [file:81][file:55]

**Important methodological note:** this repository does **not** claim that LLMs are clinically equivalent to humans or to any patient population. Clinical instruments are used here as **construct anchors**, because they operationalize the same executive dimensions in which LLMs show structured failures. [file:55]

---

## The six tasks

The benchmark covers six executive-function dimensions, each tied to a concrete neuropsychological failure mode. [file:81][file:55]

| Task | Name | Primary EF dimension | Clinical basis | Canonical failure mode |
|---|---|---|---|---|
| T1 | RuleShift / ReglaShift | Inhibitory control | BADS Rule Shift Cards [file:81][file:55] | Perseveration on the previous rule [file:81][file:55] |
| T2 | ZooMap / MapaZoo | Look-ahead planning | BADS Zoo Map Test [file:81][file:55] | Greedy local choice, downstream constraint failure [file:81][file:55] |
| T3 | SixElements / SixElementos | Prospective memory / strategic management | BADS Six Elements [file:81][file:55] | Task monopolization, poor interleaving, coverage neglect [file:81][file:55] |
| T4 | SystSearch / BúsquedaSist | Monitoring / systematic search | BADS Key Search [file:81][file:55] | Non-systematic coverage and omissions [file:81][file:55] |
| T5 | TrailBench | Alternation flexibility / set shifting | Trail Making Test Part B adaptation [file:81][file:70] | Single-set collapse, alternation failure [file:81][file:70] |
| T6 | MemEsp-Dual | Visuospatial working memory under dual-task load | CANTAB Spatial Working Memory paradigm [file:55] | Spatial tracking error plus arithmetic degradation [file:55] |

---

## Why the tasks are dissociable

Some tasks look similar on the surface but probe different executive mechanisms. This distinction is central to the benchmark. [file:55]

- **T1 vs T5:** both involve managing rules or sets, but T1 measures suppressing an old rule, while T5 measures keeping **two active sets simultaneously** and alternating correctly between them. Miyake et al. treats inhibition and shifting as related but distinct factors. [file:55]
- **T5 vs T6:** both load working memory, but T5 stresses alternation and central executive coordination, whereas T6 stresses visuospatial tracking plus simultaneous arithmetic maintenance. [file:55]

This is why a single “reasoning score” is not enough. ExProf-Bench is designed to surface **component-level breakdowns** instead of collapsing everything into generic capability. [file:55]

---

## Evaluator design

All evaluators follow the same core design principles. [file:55]

1. **100% deterministic scoring.** Every item is scored in Python against precomputed ground truth. [file:55]
2. **No LLM-as-judge.** There is no semantic similarity scoring, preference model, or heuristic grader. [file:55]
3. **Self-correction is penalized.** If a model first commits an executive error and then visibly revises itself, the item is still treated as a failure, mirroring neuropsychological scoring practice. [file:55]
4. **Axis-aware scoring.** When needed, task scores decompose into interpretable error components rather than binary success alone. [file:55]

This is a major design choice: ExProf-Bench measures the model’s **first committed executive response**, not its ability to repair itself after drifting. [file:55]

---

## Cognitive traps

Each task includes structured traps that activate the target executive dimension while also introducing secondary load from other executive processes. This cross-load architecture is intentional. [file:55]

Examples include:

- **T1 RuleShift:** hidden rule changes, adversarial reaffirmation of the old rule, conflicting authority memos, and perseveration monitoring variants. [file:68]
- **T2 ZooMap:** forbidden nodes, required nodes, ordered visits, shortest-path constraints, working-memory overload, semantic interference, and perseveration loops. [file:69][file:55]
- **T5 TrailBench:** explicit labels, abstract divisions, negative amounts, dual-allocation events, and mid-sequence rule changes under critical overrides. [file:70]

Because executive functions interact in real life, ExProf-Bench does not try to create “pure-process” toy tasks. Instead, it blocks shortcuts by embedding realistic mixed-load demands. [file:55]

---

## Executive Profile Index (EPI)

The global benchmark score is the **Executive Profile Index (EPI)**, where lower is better. [file:81][file:55]

\[
EPI = \frac{TEI + PV + (1-TSO) + (1-IS) + TVR + \frac{ER + (1-PD)}{2}}{6}
\]

[file:55]

Where:

- **TEI** = Task-set Error Index from **T1**. [file:81][file:55]
- **PV** = Protocol Violation rate from **T2**. [file:81][file:55]
- **TSO** = Task Sequence Optimization score from **T3**. [file:81][file:55]
- **IS** = Systematicity Index from **T4**. [file:81][file:55]
- **TVR** = Trail Violation Rate from **T5**. [file:81][file:70]
- **ER** and **PD** = spatial error rate and arithmetic precision from **T6**. [file:55]

### EPI interpretation

- **EPI = 0.00** means perfect performance across all six dimensions. [file:81][file:55]
- **EPI = 1.00** means complete failure on every dimension. [file:81][file:55]
- **Healthy adult reference:** approximately **0.20** based on BRIEF-2A normative orientation. [file:81][file:55]
- **Values above 0.40** fall in the mild executive dysfunction range as an orienting reference, not a diagnostic claim. [file:81][file:55]

---

## Passing criteria

At the task level, ExProf-Bench uses a **0.70 pass threshold**. A model passes a task if its item-level success rate reaches or exceeds 70%. This threshold was calibrated to preserve discriminative power and avoid benchmark saturation. [file:81][file:55]

The repository materials note that no pilot model exceeded 65% without explicit formatting cues, which helped motivate the final threshold. [file:81][file:55]

---

## Main empirical findings

### 1. Strong models do not dominate uniformly

The benchmark reveals a **jagged frontier**. Some frontier models saturate easier executive dimensions, but their rank order changes sharply when the task probes alternation flexibility or executive interference. [file:81]

### 2. T5 TrailBench is the strongest discriminator

Among the six tasks, **T5 TrailBench** shows the largest variance across models and the clearest separation between apparently similar systems. In the consolidated repository summary, T5 has: [file:81]

- **Mean pass rate:** 0.505 [file:81]
- **Range:** 0.0 to 1.0 [file:81]
- **Standard deviation:** 0.407 [file:81]

That makes T5 the task that most strongly exposes whether a model can maintain and alternate between active cognitive sets instead of collapsing into one. [file:81][file:70]

### 3. Larger is not always better

One of the headline results is a discontinuity inside the GPT-OSS family: **GPT-OSS-120B scores 0.40 on T5, while GPT-OSS-20B scores 0.95**. This directly supports the claim that parameter count alone does not predict executive-control capacity. [file:81]

### 4. Frontier saturation is selective

According to the consolidated results, some tasks are relatively easy for top models while others remain discriminative: [file:81]

| Task | Mean | Range | Std. Dev. | Interpretation |
|---|---:|---:|---:|---|
| T2 Planning | 0.878 [file:81] | 0.37–1.0 [file:81] | 0.149 [file:81] | Easiest overall [file:81] |
| T4 Monitoring | 0.942 [file:81] | 0.0–1.0 [file:81] | 0.193 [file:81] | Easy for frontier models [file:81] |
| T6 Working Memory | 0.853 [file:81] | 0.12–1.0 [file:81] | 0.201 [file:81] | Moderate [file:81] |
| T1 Inhibition | 0.731 [file:81] | 0.0–1.0 [file:81] | 0.196 [file:81] | Moderate [file:81] |
| T3 Prospective Memory | 0.889 [file:81] | 0.0–1.0 [file:81] | 0.252 [file:81] | High variance [file:81] |
| T5 Flexibility | 0.505 [file:81] | 0.0–1.0 [file:81] | 0.407 [file:81] | Strongest discriminator [file:81] |

---

## Current leaderboard snapshot

The consolidated repository summary reports the following headline leaderboard result: **Gemini-3.1-Pro** and **Gemma-4-31B** are tied at **0.976**, while **Gemma-3-1B** is the lowest reported model at **0.253**. [file:81]

Because the benchmark is organized around dissociable executive dimensions, this global ranking should always be interpreted together with **task-level breakdowns**, especially T5. ExProf-Bench is designed to show *how* a model fails, not only *how much*. [file:81][file:55]

---

## Repository contents

This repository is designed as the public results companion for the hackathon submission. The intended structure is: [file:81]

```text
ExProf-Bench-Results/
├── README.md
├── results/
│   ├── gedpve_leaderboard.csv
│   ├── global_leaderboard.png
│   ├── task_heatmap.png
│   └── t5_discriminator.png
└── notebooks/
    ├── exprof-bench-t1-reglashift-fixed.ipynb
    ├── exprof-bench-t2.ipynb
    ├── exprof-bench-t5-trailbench-consolidated.ipynb
    └── ...
```

The notebooks implement the task logic and evaluators, while the results assets provide the leaderboard and visual summary of the benchmark’s discriminative structure. [file:81][file:68][file:69][file:70]

---

## Task notes

### T1 — RuleShift

T1 is a rule-switching task that evaluates whether the model can abandon a previously reinforced criterion and apply a new one without perseverating. Its evaluator explicitly detects **perseverative responses**, near-perseveration, and format failures. The notebook includes multiple difficulty tiers, including adversarial variants that re-endorse the old rule immediately after announcing the new one. [file:68]

### T2 — ZooMap

T2 is a constrained route-planning task inspired by the BADS Zoo Map Test. Models must produce the **shortest valid route** while respecting required visits, forbidden nodes, and ordered constraints. The evaluator penalizes self-correction, invalid edges, cycles, ordering violations, forbidden visits, missing required nodes, and non-optimal routes. [file:69][file:55]

### T5 — TrailBench

T5 adapts the Trail Making Test Part B into a language setting. The model must alternate continuously between two active categories without collapsing into a single stream. The notebook contains 20 items spanning EASY, MEDIUM, HARD, and EXTREME conditions, including critical-override rule changes mid-sequence. Its task-level impairment metric is **TVR**, the Trail Violation Rate. [file:70]

---

## Why T5 matters so much

T5 is the benchmark’s clearest proof that executive control is not reducible to general fluency or size. The task requires **set maintenance plus alternation**, and many models that look excellent elsewhere collapse when they must preserve the alternation constraint across a full sequence. [file:81][file:70]

This is exactly the kind of dissociation the benchmark was built to detect. If a model scores well on planning and monitoring but fails T5, the result is not noise; it is evidence that the model’s executive profile is uneven and that “general intelligence” metrics can hide clinically interpretable control failures. [file:81][file:55]

---

## Limitations

This repository explicitly acknowledges several limitations. [file:55]

- The benchmark is **text-based**, whereas some of its clinical inspirations are physical or visuospatial tasks. [file:55]
- It does **not impose strong time pressure**, which likely underestimates difficulty in ecologically time-sensitive tasks. [file:55]
- Highly capable models may eventually meta-learn parts of the task structure, especially in T5 and T6. [file:55]
- Because prompts are linguistic, measured performance can partly interact with language proficiency and instruction-following style. [file:55]
- The BRIEF-2A comparison is an **orienting reference**, not a statement of clinical equivalence. [file:55]

---

## Future work

The writeup identifies several direct next steps: [file:55]

- A **token-constrained version** to better approximate temporal pressure. [file:55]
- A **multimodal extension** of tasks like T6 for closer correspondence with visuospatial clinical paradigms. [file:55]
- A **human validation study** using the same items to strengthen construct calibration and refine interpretation of EPI. [file:55]

---

## Recommended citation

If you use this repository, cite it as the public technical appendix for the ExProf-Bench Kaggle × Google DeepMind AGI Hackathon submission. The repository consolidates the benchmark rationale, task structure, evaluator principles, and main empirical findings. [file:81][file:55]

Suggested plain-text citation:

**Duarte, G. E. (2026). ExProf-Bench-Results: Systematic assessment of executive control in large language models. Public results repository for the Kaggle × Google DeepMind AGI Hackathon 2026.** [file:81][file:55]

---

## References

- Miyake, A., Friedman, N. P., Emerson, M. J., Witzki, A. H., Howerter, A., & Wager, T. D. (2000). *The Unity and Diversity of Executive Functions and Their Contributions to Complex “Frontal Lobe” Tasks.* Cognitive Psychology. [file:55][file:81]
- Wilson, B. A., Alderman, N., Burgess, P. W., Emslie, H., & Evans, J. J. (1996). *BADS: Behavioural Assessment of the Dysexecutive Syndrome.* [file:55][file:81]
- PAR Inc. (2024). *BRIEF-2A Behavior Rating Inventory of Executive Function, Adult Version.* Normative adult sample n=1,637. [file:55][file:81]
- Baddeley, A. (2000). *The episodic buffer: A new component of working memory?* Trends in Cognitive Sciences. [file:55]
- de Langis, K. et al. (2026). *Strong Memory, Weak Control: An Empirical Study of Executive Functioning in LLMs.* [file:55]
- Song, P. et al. (2024). *In-Context Learning May Not Elicit Trustworthy Reasoning: A-Not-B Errors in Pretrained Language Models.* EMNLP Findings. [file:55]
- Upadhayay, B. et al. (2025). *Working Memory Attack on LLMs.* ICLR 2025. [file:55]
- LeCun, Y. (2022). *A Path Toward Autonomous Machine Intelligence.* [file:55]

---

## Status

This repository serves as the **complete public appendix** to the ExProf-Bench submission. The main added value relative to the rushed competition writeup is that it preserves the full benchmark logic: the clinical grounding, the EPI derivation, the 33-model leaderboard, the T5 discontinuity result, and the argument that executive control in LLMs forms a jagged frontier rather than a smooth scale. [file:81]
