# ExProf-Bench-Results

**ExProf-Bench** is a clinically informed benchmark for measuring executive control failures in large language models, grounded in validated executive-function constructs without claiming diagnostic or mechanistic equivalence to humans.It was developed for the **Kaggle × Google DeepMind AGI Hackathon 2026 — Track: Executive Functions** and evaluates whether a model can coordinate cognition under competing constraints, not merely retrieve knowledge.

This repository is the **complete technical appendix and public results companion** to the hackathon submission. It includes the benchmark rationale, the six-task architecture, the Executive Profile Index (EPI), consolidated findings, and the main empirical result: a **jagged frontier** in executive control, where larger models do not reliably dominate smaller ones across dissociable executive-function dimensions.

---

## Why this benchmark exists

Most current LLM benchmarks reward retrieval, pattern completion, or broad problem-solving competence. ExProf-Bench instead asks a narrower and more important question: **can a model maintain, inhibit, switch, monitor, and coordinate task sets under pressure and interference?**

The benchmark is motivated by converging evidence that LLMs can show strong memory or fluent language behavior while failing in tasks that require **fluid executive control**, especially under rule shifts, dual-task load, and interference. The theoretical framing in this repository draws directly on the executive-function literature and on recent LLM studies documenting memory-control dissociations and perseverative failures.

---

## Core contribution

ExProf-Bench contributes three things:

- A **6-task executive-function benchmark** grounded in clinical neuropsychology rather than generic reasoning prompts.
- A **fully deterministic scoring pipeline** with 100 Python evaluators and no LLM-as-judge component.
- A global impairment metric, the **Executive Profile Index (EPI)**, that turns dissociable failures into a single interpretable score while preserving task-level diagnostic meaning.

The central empirical finding is that frontier performance is **not smooth**. Several tasks saturate for strong models, but **T5 TrailBench** sharply re-separates the field and reveals a discontinuous executive-control ceiling.

---

## Benchmark summary

| Property | Value |
|---|---|
| Track | Kaggle × Google DeepMind AGI Hackathon 2026, Executive Functions |
| Tasks | 6 dissociable executive-function tasks |
| Total items | 150 items |
| Evaluators | 100 deterministic Python evaluators |
| Judging | No LLM judge, no embedding similarity, no probabilistic scoring |
| Models evaluated | 33 models |
| Output focus | Pass rate by task, cross-task profile, global EPI |

---

## Theoretical framework

ExProf-Bench is structured around the **Unity-and-Diversity** model of executive functions proposed by **Miyake et al. (2000)**, which distinguishes related but separable executive processes such as inhibition, shifting, and updating. The benchmark uses that framework to justify six tasks that are cognitively related but empirically dissociable. 

Two clinical anchors guide the construct design and interpretation:

- **BADS** (*Behavioural Assessment of the Dysexecutive Syndrome*) provides the structural basis for T1, T2, T3, and T4.
- **BRIEF-2A** provides the normative adult reference used to orient interpretation of aggregate executive impairment. Its adult norm sample is **n = 1,637**.

**Important methodological note:** this repository does **not** claim that LLMs are clinically equivalent to humans or to any patient population. Clinical instruments are used here as **construct anchors**, because they operationalize the same executive dimensions in which LLMs show structured failures. 

---

## The six tasks

The benchmark covers six executive-function dimensions, each tied to a concrete neuropsychological failure mode.

| Task | Name | Primary EF dimension | Clinical basis | Canonical failure mode |
|---|---|---|---|---|
| T1 | RuleShift / ReglaShift | Inhibitory control | BADS Rule Shift Cards | Perseveration on the previous rule |
| T2 | ZooMap / MapaZoo | Look-ahead planning | BADS Zoo Map Test | Greedy local choice, downstream constraint failure |
| T3 | SixElements / SixElementos | Prospective memory / strategic management | BADS Six Elements | Task monopolization, poor interleaving, coverage neglect  |
| T4 | SystSearch / BúsquedaSist | Monitoring / systematic search | BADS Key Search | Non-systematic coverage and omissions |
| T5 | TrailBench | Alternation flexibility / set shifting | Trail Making Test Part B adaptation | Single-set collapse, alternation failure |
| T6 | MemEsp-Dual | Visuospatial working memory under dual-task load | CANTAB Spatial Working Memory paradigm | Spatial tracking error plus arithmetic degradation |

---

## Why the tasks are dissociable

Some tasks look similar on the surface but probe different executive mechanisms. This distinction is central to the benchmark. 

- **T1 vs T5:** both involve managing rules or sets, but T1 measures suppressing an old rule, while T5 measures keeping **two active sets simultaneously** and alternating correctly between them. Miyake et al. treats inhibition and shifting as related but distinct factors. 
- **T5 vs T6:** both load working memory, but T5 stresses alternation and central executive coordination, whereas T6 stresses visuospatial tracking plus simultaneous arithmetic maintenance. 

This is why a single “reasoning score” is not enough. ExProf-Bench is designed to surface **component-level breakdowns** instead of collapsing everything into generic capability.

---

## Evaluator design

All evaluators follow the same core design principles. 

1. **100% deterministic scoring.** Every item is scored in Python against precomputed ground truth.
2. **No LLM-as-judge.** There is no semantic similarity scoring, preference model, or heuristic grader.
3. **Self-correction is penalized.** If a model first commits an executive error and then visibly revises itself, the item is still treated as a failure, mirroring neuropsychological scoring practice.
4. **Axis-aware scoring.** When needed, task scores decompose into interpretable error components rather than binary success alone.

This is a major design choice: ExProf-Bench measures the model’s **first committed executive response**, not its ability to repair itself after drifting.

---

## Cognitive traps

Each task includes structured traps that activate the target executive dimension while also introducing secondary load from other executive processes. This cross-load architecture is intentional.

Examples include:

- **T1 RuleShift:** hidden rule changes, adversarial reaffirmation of the old rule, conflicting authority memos, and perseveration monitoring variants.
- **T2 ZooMap:** forbidden nodes, required nodes, ordered visits, shortest-path constraints, working-memory overload, semantic interference, and perseveration loops.
- **T5 TrailBench:** explicit labels, abstract divisions, negative amounts, dual-allocation events, and mid-sequence rule changes under critical overrides.

Because executive functions interact in real life, ExProf-Bench does not try to create “pure-process” toy tasks. Instead, it blocks shortcuts by embedding realistic mixed-load demands.

---

## Executive Profile Index (EPI)

The global benchmark score is the **Executive Profile Index (EPI)**, where lower is better.


$$EPI = \frac{TEI + PV + (1-TSO) + (1-IS) + TVR + \frac{ER + (1-PD)}{2}}{6}$$



| Componente | Tarea | Interpretación |
|---|---|---|
| **TEI** | T1 RuleShift | Task-set Error Index |
| **PV** | T2 ZooMap | Protocol Violation rate |
| **1-TSO** | T3 SixElements | Task Sequence Optimization |
| **1-IS** | T4 SystSearch | Inverse Systematicity Index |
| **TVR** | T5 TrailBench | Trail Violation Rate |
| **(ER + (1-PD))/2** | T6 MemEsp-Dual | Dual-task composite |


### EPI interpretation

- **EPI = 0.00** means perfect performance across all six dimensions. 
- **EPI = 1.00** means complete failure on every dimension. 
- **Healthy adult reference:** approximately **0.20** based on BRIEF-2A normative orientation. 
- **Values above 0.40** fall in the mild executive dysfunction range as an orienting reference, not a diagnostic claim.

---

## Passing criteria

At the task level, ExProf-Bench uses a **0.70 pass threshold**. A model passes a task if its item-level success rate reaches or exceeds 70%. This threshold was calibrated to preserve discriminative power and avoid benchmark saturation. 

The repository materials note that no pilot model exceeded 65% without explicit formatting cues, which helped motivate the final threshold. 

---

## Main empirical findings

### 1. Strong models do not dominate uniformly

The benchmark reveals a **jagged frontier**. Some frontier models saturate easier executive dimensions, but their rank order changes sharply when the task probes alternation flexibility or executive interference. 

### 2. T5 TrailBench is the strongest discriminator

Among the six tasks, **T5 TrailBench** shows the largest variance across models and the clearest separation between apparently similar systems. In the consolidated repository summary, T5 has: 

- **Mean pass rate:** 0.505 
- **Range:** 0.0 to 1.0 
- **Standard deviation:** 0.407 

That makes T5 the task that most strongly exposes whether a model can maintain and alternate between active cognitive sets instead of collapsing into one. 

### 3. Larger is not always better

One of the headline results is a discontinuity inside the GPT-OSS family: **GPT-OSS-120B scores 0.40 on T5, while GPT-OSS-20B scores 0.95**. This directly supports the claim that parameter count alone does not predict executive-control capacity. 

### 4. Frontier saturation is selective

According to the consolidated results, some tasks are relatively easy for top models while others remain discriminative: 

| Task | Mean | Range | Std. Dev. | Interpretation |
|---|---:|---:|---:|---|
| T2 Planning | 0.878 | 0.37–1.0 | 0.149 | Easiest overall  |
| T4 Monitoring | 0.942 | 0.0–1.0 | 0.193 | Easy for frontier models |
| T6 Working Memory | 0.853 | 0.12–1.0 | 0.201 | Moderate |
| T1 Inhibition | 0.731 | 0.0–1.0 | 0.196 | Moderate |
| T3 Prospective Memory | 0.889 | 0.0–1.0 | 0.252 | High variance |
| T5 Flexibility | 0.505 | 0.0–1.0 | 0.407 | Strongest discriminator |

---

## Current leaderboard snapshot

The consolidated repository summary reports the following headline leaderboard result: **Gemini-3.1-Pro** and **Gemma-4-31B** are tied at **0.976**, while **Gemma-3-1B** is the lowest reported model at **0.253**.

Because the benchmark is organized around dissociable executive dimensions, this global ranking should always be interpreted together with **task-level breakdowns**, especially T5. ExProf-Bench is designed to show *how* a model fails, not only *how much*.
---

## Repository contents

This repository is designed as the public results companion for the hackathon submission. The intended structure is:

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

The notebooks implement the task logic and evaluators, while the results assets provide the leaderboard and visual summary of the benchmark’s discriminative structure.
---

## Task notes

### T1 — RuleShift

T1 is a rule-switching task that evaluates whether the model can abandon a previously reinforced criterion and apply a new one without perseverating. Its evaluator explicitly detects **perseverative responses**, near-perseveration, and format failures. The notebook includes multiple difficulty tiers, including adversarial variants that re-endorse the old rule immediately after announcing the new one. 

### T2 — ZooMap

T2 is a constrained route-planning task inspired by the BADS Zoo Map Test. Models must produce the **shortest valid route** while respecting required visits, forbidden nodes, and ordered constraints. The evaluator penalizes self-correction, invalid edges, cycles, ordering violations, forbidden visits, missing required nodes, and non-optimal routes. 

### T5 — TrailBench

T5 adapts the Trail Making Test Part B into a language setting. The model must alternate continuously between two active categories without collapsing into a single stream. The notebook contains 20 items spanning EASY, MEDIUM, HARD, and EXTREME conditions, including critical-override rule changes mid-sequence. Its task-level impairment metric is **TVR**, the Trail Violation Rate.

---

## Why T5 matters so much

T5 is the benchmark’s clearest proof that executive control is not reducible to general fluency or size. The task requires **set maintenance plus alternation**, and many models that look excellent elsewhere collapse when they must preserve the alternation constraint across a full sequence. 

This is exactly the kind of dissociation the benchmark was built to detect. If a model scores well on planning and monitoring but fails T5, the result is not noise; it is evidence that the model’s executive profile is uneven and that “general intelligence” metrics can hide clinically interpretable control failures. 

---

## Limitations

This repository explicitly acknowledges several limitations.

- The benchmark is **text-based**, whereas some of its clinical inspirations are physical or visuospatial tasks.
- It does **not impose strong time pressure**, which likely underestimates difficulty in ecologically time-sensitive tasks.
- Highly capable models may eventually meta-learn parts of the task structure, especially in T5 and T6.
- Because prompts are linguistic, measured performance can partly interact with language proficiency and instruction-following style.
- The BRIEF-2A comparison is an **orienting reference**, not a statement of clinical equivalence.

---

## Future work

The writeup identifies several direct next steps: 

- A **token-constrained version** to better approximate temporal pressure. 
- A **multimodal extension** of tasks like T6 for closer correspondence with visuospatial clinical paradigms. 
- A **human validation study** using the same items to strengthen construct calibration and refine interpretation of EPI.

---

## Recommended citation

If you use this repository, cite it as the public technical appendix for the ExProf-Bench Kaggle × Google DeepMind AGI Hackathon submission. The repository consolidates the benchmark rationale, task structure, evaluator principles, and main empirical findings. 

Suggested plain-text citation:

**Duarte, G. E. (2026). ExProf-Bench-Results: Systematic assessment of executive control in large language models. Public results repository for the Kaggle × Google DeepMind AGI Hackathon 2026.**

---

## References

- Miyake, A., Friedman, N. P., Emerson, M. J., Witzki, A. H., Howerter, A., & Wager, T. D. (2000). *The Unity and Diversity of Executive Functions and Their Contributions to Complex “Frontal Lobe” Tasks.* Cognitive Psychology.
- Wilson, B. A., Alderman, N., Burgess, P. W., Emslie, H., & Evans, J. J. (1996). *BADS: Behavioural Assessment of the Dysexecutive Syndrome.*
- PAR Inc. (2024). *BRIEF-2A Behavior Rating Inventory of Executive Function, Adult Version.* Normative adult sample n=1,637. 
- Baddeley, A. (2000). *The episodic buffer: A new component of working memory?* Trends in Cognitive Sciences.
- de Langis, K. et al. (2026). *Strong Memory, Weak Control: An Empirical Study of Executive Functioning in LLMs.* 
- Song, P. et al. (2024). *In-Context Learning May Not Elicit Trustworthy Reasoning: A-Not-B Errors in Pretrained Language Models.* EMNLP Findings.
- Upadhayay, B. et al. (2025). *Working Memory Attack on LLMs.* ICLR 2025. 
- LeCun, Y. (2022). *A Path Toward Autonomous Machine Intelligence.* 

---

## Status

This repository serves as the **complete public appendix** to the ExProf-Bench submission. The main added value relative to the rushed competition writeup is that it preserves the full benchmark logic: the clinical grounding, the EPI derivation, the 33-model leaderboard, the T5 discontinuity result, and the argument that executive control in LLMs forms a jagged frontier rather than a smooth scale.
