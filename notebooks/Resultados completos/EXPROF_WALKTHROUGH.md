# ExProf-Bench — Methodological Walkthrough

> **ExProf-Bench v1.0** — Executive-function benchmark for large language models (LLMs).
> Evaluates not general accuracy, but the integrity of executive processes under high cognitive demand.

---

## 1. Why an executive-function benchmark

Existing reasoning benchmarks (MMLU, HumanEval, GSM8K) measure declarative ability or domain-specific skills. They do not capture whether a model can **maintain goals under interference**, **inhibit prior responses when rules change**, **plan sequences without overlap**, or **run two tasks in parallel without degradation**.

These capabilities correspond to **executive functions (EF)**: high-level control processes that in neuropsychology distinguish between general intelligence and operative cognitive efficiency. A model can achieve high accuracy on factual questions and collapse completely on tasks demanding executive control.

ExProf-Bench fills that gap.

---

## 2. Empirical reference framework: BADS and BRIEF-2A

The benchmark design draws on two population-validated cognitive assessment instruments — not to diagnose models, but to **calibrate tasks and performance thresholds** against real human evidence.

### BADS — Behavioural Assessment of the Dysexecutive Syndrome (Wilson et al., 1996)

A battery designed to measure executive control in **ecological** conditions — complex functional situations with multiple simultaneous constraints, not atomic lab tests. The principle ExProf-Bench adopts: executive-control failures emerge when planning demand, monitoring, and adaptation co-occur in the same scenario. That is exactly what LLMs face in these tasks.

Tasks T2 (Zoo Map), T3 (Six Elements), and T5 (Trail Bench) are direct adaptations of BADS subtasks.

### BRIEF-2A — Behavior Rating Inventory of Executive Function, Adult (Gioia et al.)

Provides the **normative anchors** for EPI-5. Thresholds are derived from human population norms (n = 1,637 adults), allowing model performance to be placed on an externally calibrated scale — rather than comparing models only against each other:

| EPI-5 Pass Rate | Adult reference (BRIEF-2A, n = 1,637) | ExProf-Bench tier |
|:---|:---|:---|
| ≥ 0.70 | Executive performance within expected range | **Functional** |
| 0.40 – 0.70 | Performance at the lower end of expected range | **Borderline** |
| < 0.40 | Performance below expected range for adults | **Executive Impairment** |

> **Methodological note:** BRIEF-2A thresholds are an external reference scale, not a diagnosis. "Executive Impairment" describes model performance on these tasks — it does not attribute any condition to the model. It is equivalent to saying that the model's output on these dimensions falls below the expected normative range for adults.

---

## 3. The six tasks: design and rationale

| Task | Executive function | Metric | Clinical reference | Status |
|:---|:---|:---|:---|:---|
| **T1 — Rule Shift** | Cognitive flexibility | TEI (Task-set Error Index) | WCST, Trail Making B | ✅ Active |
| **T2 — Zoo Map** | Spatial planning under constraints | PV (Protocol Violation rate) | BADS Zoo Map Test | ✅ Active |
| **T3 — Six Elements** | Multi-task sequential planning | 1 − TSO (Task Sequence Optimization) | BADS Modified Six Elements | ✅ Active |
| **T4 — Zone Alias / GMUD** | Monitoring / distractor suppression | 1 − IS (Systematicity Index) | CANTAB SWM | ❌ Excluded |
| **T5 — Trail Bench** | Fluid intelligence / working memory | TVR (Trail Violation Rate) | Raven's, TMT | ✅ Active |
| **T6 — MemEsp-Dual** | Dual-task maintenance | (ER + (1−PD)) / 2 | Dual-task paradigms | ✅ Active |

### Task logic

**T1 (Rule Shift / Flexibility):** The model learns a classification rule; then, without explicit warning, the rule changes and it must apply the new one. Perseveration errors — continuing to use the prior rule — are the impairment signal. Metric: perseverative error rate (TEI).

**T2 (Zoo Map / Planning):** The model must trace a route satisfying multiple simultaneous constraints. The shortest path typically violates at least one constraint. The task measures whether the model plans globally before acting or follows a greedy path. Metric: protocol violation rate (PV).

**T3 (Six Elements / Sequencing):** The model distributes effort across 6 subtasks with the constraint that no two subtasks of the same type may be worked consecutively. Sequence optimization is the signal. Metric: proportion of unique subtasks completed in a valid sequence (TSO).

**T5 (Trail Bench / Executive Fluency):** An adaptation of the Trail Making Test. The model alternates between two sequences under increasing load. Metric: trail violation rate (TVR). The most discriminative task in the benchmark.

**T6 (MemEsp-Dual / Dual-task):** The model runs two tasks in parallel. Both error rate (ER) and precision loss on the secondary task (PD) are measured. Each task alone may be trivial; simultaneous demand reveals attentional allocation capacity.

---

## 4. The EPI index: construction and formula

The **Executive Performance Impairment (EPI)** aggregates per-task metrics into a single impairment index:

- **0** = no detectable executive impairment across evaluated tasks
- **1** = total failure on every dimension

The formula is the average of the per-task impairment indices. Each component is already normalized to [0, 1] with the convention: **higher value = greater impairment**.

---

## 5. The T4 case: why it was excluded

### 5.1 Original design — Zone Alias Trap

T4 was designed to measure distractor suppression via a systematic search paradigm with semantic traps. The model had to traverse zones in boustrophedon order while ignoring intentionally confusing zone aliases.

### 5.2 Empirical result across 33 models

| Statistic | T4 | Reference (T5) |
|:---|:---|:---|
| Global mean | 49.1% | varies by model |
| Standard deviation | **9.6%** | ~34% |
| Observed range | 0 – 58.8% | wide |

Every model — from 1B to 480B parameters — converged to the 50–58% range. The task was statistically indistinguishable from chance. It did not discriminate.

### 5.3 Redesign attempt — GMUD (Goal Maintenance Under Distraction)

Following the failure of the original T4, an alternative version was designed based on the **Silent Stroop** paradigm: the model had to perform a boustrophedon scan on 3×3 to 6×6 grids while the context included emergency telemetry designed to capture its attention and interrupt the primary goal. The conflict was implicit — there was no explicit instruction to ignore the emergency.

**Pilot result (Gemini 3 Flash Preview, 20 items):** 20/20 (100%), score = 1.000 on every item, I² = 0.000. Zero detectable interference at any difficulty level.

### 5.4 Why the redesign also failed: the architectural argument

The Stroop task works in humans because **reading is automatic**: the brain processes the word "RED" involuntarily even when the instruction is to report the ink color. Inhibiting that pre-activated response requires active cognitive effort, and that effort produces measurable errors and latencies.

This automaticity is well documented. **MacLeod (1991)**, in his half-century review of Stroop research (*Psychological Bulletin*, 109(2), 163–203), establishes that interference occurs precisely because reading is a **pre-attentive, parallel, and unstoppable** process once triggered. **Shiffrin & Schneider (1977)** (*Psychological Review*, 84(2), 127–190) define automatic processes as those that execute without intention, without consuming attentional resources, and that cannot be voluntarily suppressed — it is that unstoppability that creates the conflict.

LLMs **do not have that mechanism**. The reason is not that they are better at inhibiting — it is that the structural conflict never exists:

1. **The forward pass is atomic:** the entire input — instruction, context, distractors — is processed in parallel by the self-attention mechanism (Vaswani et al., 2017, *NeurIPS*). There is no "prior automatic stage" that fires before the instruction arrives.
2. **There is no already-activated response to suppress:** in human Stroop, the system is already reading "RED" while trying to respond "blue." In an LLM, the distractor is simply more tokens in the context — processed uniformly, with no preferential activation.
3. **Suppression occurs in latent space, with no behavioral trace:** if one internal representation competes with another, that conflict resolves inside the model without producing the observable error-and-interference pattern that defines measurable inhibitory control.
4. **Training eliminates the conflict at the root:** LLMs were optimized to follow written instructions. There is no automatic response competing with the instruction, because following written instructions *is* the trained behavior.

The conclusion is not that LLMs "resist distraction well." It is that **the parallel inference architecture eliminates the precondition for inhibitory control**. The effect fails not because the model is very good at inhibiting — it fails because there is never anything to inhibit.

Converging empirical evidence: **Cognitive Control in Vision-Language Models** (arXiv:2505.18969, 2025) documents that observable executive-control failures in LLMs are selective and structural, not a general degradation. **Deficient Executive Control in Transformer Attention** (bioRxiv, 2025) proposes that certain control failures emerge from the attention architecture, not model capacity. Both agree that executive-control failures in LLMs are **construct-specific** — some are measurable and real; others are architecturally impossible to replicate.

### 5.5 Why T1 is evaluable via text

T4 was excluded because the automatic inhibition it demands cannot exist in an LLM — that argument is developed in the previous section. A natural follow-up question is: **should T1 also be excluded? It also carries the "Inhibition" label.**

The answer is no, because T1 measures an operationally distinct construct.

**T1 does not measure automatic inhibition.** It measures **perseveration resistance**: the model learns and applies a classification rule; the context then changes and the model must stop applying the old rule and adopt the new one. The observable failure is continuing to use the obsolete rule. This construct is evaluable via text because:

1. Both the old rule and the new rule are represented **explicitly** in the input.
2. The "conflict" is between the model's statistical tendency to continue the prior pattern and the explicit instruction to change — not between an already-activated automatic process and a conscious one.
3. Both the stimulus and the correct response are fully encoded in text. No processing outside the context window is required.
4. Errors are observable and quantifiable: the model produces the response of the old rule when it should produce the response of the new one.

The precise construct is **cognitive set shifting**: disengaging from an active pattern and adopting a new one. The TEI metric (Task-set Error Index) measures exactly that: the perseverative error rate.

**Terminological note:** T1 inherits the "Inhibition" label from its clinical analogue (BADS Rule Shift Cards), which the literature groups under the broad inhibitory construct. That label is correct in the sense that perseverating = failing to inhibit the old rule — but the mechanism does not require pre-attentive processing, which is the precondition that makes T4 non-viable. Any benchmark that uses "inhibitory control" without distinguishing between the two mechanisms is conflating constructs that ExProf-Bench separates operationally.

- **T2** captures the tendency toward **greedy path selection**: the model follows the shortest route even when that route violates constraints — resistance to the statistical prior, also evaluable via text for the same reason as T1.

In both cases, what generates variance across models is **resistance to the dominant statistical prior**: a measurable, real construct in LLMs, operationally distinct from the automatic inhibition whose architectural absence justified excluding T4.

### 5.6 Can inhibitory control be measured via prompting?

A legitimate question is whether any prompting design can validly measure inhibition in LLMs. The short answer is no — at least not inhibition in the strict sense.

The paradigm that comes closest is **cumulative semantic inversion**: giving rules that invert word meanings and asking questions that activate strong semantic priors, stacking inversion layers until the model collapses. This creates real variance across models. However, what it measures is not inhibition — it measures **working memory under rule load**. When the model fails at the third or fourth inversion level, it fails because it lost track of the active rules, not because an automatic impulse overcame it. That is precisely what T5 of the benchmark measures.

Inhibitory control requires three conditions that prompting cannot satisfy simultaneously:

1. An automatic response already activated before the control system intervenes
2. A mechanism that actively halts it during execution
3. Observable behavioral evidence of that conflict (errors or differential latency)

No prompting paradigm activates an automatic response in the biological sense. It activates a statistically learned response and asks for a substitution — that is rule-following, not inhibition. An incorrect output could stem from inhibitory failure, working-memory failure, or comprehension failure. They are indistinguishable from the outside.

**Conclusion:** No prompting paradigm cleanly measures inhibitory control in LLMs. What any benchmark claiming to measure it actually measures is resistance to statistical priors, rule-following under load, or working memory — valid and interesting constructs, but not inhibition in the strict sense. Labeling them "inhibitory control" is construct relabeling.

---

## 6. Official formula: EPI-5

With T4 excluded, the official index is:

```
EPI-5 = (T1_imp + T2_imp + T3_imp + T5_imp + T6_imp) / 5
```

Each component is the impairment index for that task: `0 = optimal, 1 = total failure`.

### Impact of exclusion on discrimination

| Metric | EPI-6 (with T4) | EPI-5 (without T4) |
|:---|:---|:---|
| Global mean | 0.1849 | 0.1966 |
| Standard deviation | 0.1496 | **0.1602** |
| Range | 0.6765 | 0.6737 |
| Coefficient of variation | 0.8089 | **0.8152** |

Standard deviation increased 7%. The improvement is not dramatic because T1–T3, T5, and T6 always discriminated correctly — the problem was specifically T4, which added random noise. EPI-5 is cleaner, not radically different in dispersion.

A real effect is visible in the **distribution**: **3 models that appeared in Functional under EPI-6 moved to Borderline under EPI-5** — GPT-5.4 nano (0.734→0.693), Gemma 3 12B (0.717→0.680), and Claude Haiku 4.5 (0.702→0.660). In all three cases, T4 — converging at ~100% by chance for these models — was artificially inflating their pass rate and masking genuine weakness on T5 and T6. Removing T4 correctly reclassifies them.

---

## 7. Full leaderboard — 33 models

**Classification by EPI-5 pass rate (mean T1–T3, T5, T6):**
- 🟢 **Functional** — pass rate ≥ 0.70 (27 models)
- 🟡 **Borderline** — pass rate 0.40–0.70 (4 models)
- 🔴 **Executive Impairment** — pass rate < 0.40 (2 models)

| # | Model | EPI-5 | EPI-6 ref | T1 | T2 | T3 | T5 | T6 | Tier |
|:---|:---|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---|
| 1 | Gemini 3.1 Pro Preview | **0.034** | 0.041 | 85.7 | 100.0 | 100.0 | 100.0 | 97.5 | 🟢 Functional |
| 2 | Gemma 4 31B | **0.034** | 0.041 | 85.7 | 100.0 | 100.0 | 100.0 | 97.3 | 🟢 Functional |
| 3 | Qwen 3 Next 80B Thinking | **0.036** | 0.049 | 85.7 | 100.0 | 100.0 | 100.0 | 96.1 | 🟢 Functional |
| 4 | Claude Sonnet 4 | 0.047 | 0.058 | 85.7 | 92.3 | 100.0 | 100.0 | 98.4 | 🟢 Functional |
| 5 | Gemma 4 26B A4B | 0.056 | 0.059 | 85.7 | 100.0 | 100.0 | 90.0 | 96.1 | 🟢 Functional |
| 6 | gpt-oss-20b | 0.057 | 0.055 | 85.7 | 93.3 | 98.0 | 97.5 | 96.8 | 🟢 Functional |
| 7 | Gemini 2.5 Pro | 0.066 | 0.065 | 74.3 | 96.7 | 100.0 | 100.0 | 96.0 | 🟢 Functional |
| 8 | Claude Sonnet 4.6 | 0.066 | 0.081 | 85.7 | 85.7 | 100.0 | 100.0 | 95.6 | 🟢 Functional |
| 9 | GLM-5 | 0.070 | 0.072 | 68.6 | 100.0 | 100.0 | 100.0 | 96.5 | 🟢 Functional |
| 10 | Claude Opus 4.5 | 0.079 | 0.081 | 68.6 | 93.3 | 100.0 | 100.0 | 98.5 | 🟢 Functional |
| 11 | Claude Sonnet 4.5 | 0.079 | 0.082 | 68.6 | 93.3 | 100.0 | 100.0 | 98.5 | 🟢 Functional |
| 12 | Claude Opus 4.6 | 0.081 | 0.114 | 68.6 | 96.7 | 100.0 | 100.0 | 94.1 | 🟢 Functional |
| 13 | GPT-5.4 | 0.092 | 0.087 | 88.6 | 86.7 | 90.0 | 92.5 | 96.4 | 🟢 Functional |
| 14 | Gemini 2.5 Flash | 0.107 | 0.107 | 85.7 | 96.7 | 100.0 | 67.5 | 96.7 | 🟢 Functional |
| 15 | Claude Opus 4.1 | 0.146 | 0.138 | 88.6 | 93.3 | 90.0 | 57.5 | 97.7 | 🟢 Functional |
| 16 | Gemini 3.1 Flash-Lite Preview | 0.193 | 0.163 | 85.7 | 89.0 | 98.0 | 32.5 | 98.1 | 🟢 Functional |
| 17 | gpt-5.4-mini-2026-03-17 | 0.200 | 0.182 | 100.0 | 81.3 | 100.0 | 30.0 | 88.8 | 🟢 Functional |
| 18 | qwen3-235b-a22b-instruct-2507 | 0.200 | 0.188 | 85.7 | 91.3 | 100.0 | 32.5 | 90.3 | 🟢 Functional |
| 19 | gemini-2.0-flash | 0.211 | 0.184 | 85.7 | 92.3 | 88.0 | 35.0 | 93.6 | 🟢 Functional |
| 20 | Gemini 3 Flash Preview | 0.213 | 0.187 | 71.4 | 100.0 | 100.0 | 25.0 | 97.3 | 🟢 Functional |
| 21 | Deepseek V3.1 | 0.225 | 0.199 | 77.1 | 90.7 | 100.0 | 30.0 | 90.0 | 🟢 Functional |
| 22 | DeepSeek V3.2 | 0.231 | 0.215 | 82.9 | 87.3 | 100.0 | 25.0 | 91.4 | 🟢 Functional |
| 23 | Qwen 3 Coder 480B | 0.237 | 0.206 | 74.3 | 94.7 | 100.0 | 27.5 | 82.8 | 🟢 Functional |
| 24 | Qwen 3 Next 80B Instruct | 0.240 | 0.215 | 88.6 | 79.7 | 100.0 | 25.0 | 86.9 | 🟢 Functional |
| 25 | gpt-oss-120b | 0.252 | 0.256 | 100.0 | 80.0 | 60.0 | 40.0 | 94.2 | 🟢 Functional |
| 26 | Gemini 2.0 Flash Lite | 0.272 | 0.238 | 88.6 | 83.7 | 100.0 | 0.0 | 91.8 | 🟢 Functional |
| 27 | Gemma 3 27B | 0.280 | 0.251 | 68.6 | 89.0 | 100.0 | 22.5 | 79.8 | 🟢 Functional |
| 28 | GPT-5.4 nano | 0.307 | 0.266 | 97.1 | 81.7 | 94.0 | 2.5 | 71.2 | 🟡 Borderline |
| 29 | Gemma 3 12B | 0.320 | 0.283 | 74.3 | 81.3 | 100.0 | 7.5 | 76.9 | 🟡 Borderline |
| 30 | Claude Haiku 4.5 | 0.340 | 0.298 | 68.6 | 97.0 | 100.0 | 0.0 | 64.2 | 🟡 Borderline |
| 31 | gemma-3-4b | 0.348 | 0.313 | 97.1 | 67.0 | 92.0 | 0.0 | 70.1 | 🟡 Borderline |
| 32 | DeepSeek-R1 ⚠️ | 0.661 | 0.717 | 34.3 | 36.7 | 0.0 | 30.0 | 68.7 | 🔴 Executive Impairment |
| 33 | Gemma 3 1B | 0.707 | 0.611 | 14.3 | 40.7 | 36.0 | 0.0 | 55.4 | 🔴 Executive Impairment |

> ⚠️ **DeepSeek-R1:** `<think>...</think>` blocks generated before the output caused false negatives in the response parser. Its impairment metrics are artificially inflated. Actual values would be lower on T1, T2, and T3.

---

## 8. Main findings

### 8.1 T5 is the primary discriminator

Fluid intelligence (T5 / Trail Bench) is the task that most separates models. The top 6 models by EPI-5 show 0% impairment on T5. From rank 14 onward, T5 becomes the bottleneck: Gemini 2.5 Flash (T5: 67.5%), Claude Opus 4.1 (T5: 57.5%), and 6 models in the bottom half of the ranking score 0% on T5.

This suggests that working-memory load under alternating sequences is the most demanding executive dimension for current LLMs.

### 8.2 The Jagged Frontier

Executive performance is neither linear nor homogeneous within a single model. Examples:

- **gemma-3-4b**: T1 = 97.1% (excellent flexibility) but T6 = 70.1% (dual-task degraded)
- **gpt-5.4-mini**: T1 = 100%, T3 = 100%, but T5 = 30% (executive fluency collapse)
- **Claude Haiku 4.5**: T2 = 97% (near-perfect planning), T5 = 0% (total trail failure)

This cross-dimension dissociation is the benchmark's most valuable characteristic: there is no "executively strong in everything" model.

### 8.3 Scale does not predict execution

Model size does not guarantee superior executive performance:
- **Gemma 4 31B** (EPI = 0.034) outperforms **Claude Opus 4.1** (EPI = 0.146)
- **Qwen 3 Coder 480B** (EPI = 0.237) ranks below **GLM-5** (EPI = 0.070)
- **gemma-3-4b** outperforms models 10× larger on T1

### 8.4 The DeepSeek-R1 artifact

DeepSeek-R1 generates `<think>...</think>` blocks before its output. The original benchmark parsers did not filter these blocks, causing false negatives: correct answers scored as incorrect. This artificially inflates its impairment metrics. Later parsers incorporated CoT filtering (`re.sub(r'<think>.*?</think>', '', response, flags=re.DOTALL)`). DeepSeek-R1 metrics in this leaderboard should be interpreted with caution.

---

## 9. What ExProf-Bench measures and what it does not

**Measures:**
- Cognitive flexibility under rule change (T1)
- Planning under multiple simultaneous constraints (T2)
- Multi-task sequence optimization (T3)
- Executive fluency under sequential load (T5)
- Dual-task maintenance without degradation (T6)

**Does not measure:**
- Stroop-type inhibition (incompatible with atomic inference architecture)
- Processing speed (latency irrelevant in this context)
- Factual accuracy or declarative knowledge
- Pure mathematical reasoning ability

---

## 10. Notes on the normative reference

BRIEF-2A thresholds are used as an external reference scale, not as a diagnosis. A model landing in "Executive Impairment" means its performance on these tasks is numerically equivalent to that of the bottom quartile of the human normative sample (n = 1,637 adults) on these executive-control dimensions. It does not imply any attribution about the model's nature nor a medical comparison.

The value of the reference is methodological: it places model performance within a continuum calibrated against real population evidence, rather than comparing models only against each other without external anchor. A model scoring EPI > 0.40 simply fails these tasks at a rate that, applied to a human, would fall below the expected normative range for adults. The model does not "have" any condition — it produces outputs that, on these dimensions, fall outside the reference range.

---

## 11. References

- Wilson, B.A. et al. (1996). *Behavioural Assessment of the Dysexecutive Syndrome (BADS)*. Thames Valley Test Company.
- Gioia, G.A. et al. *Behavior Rating Inventory of Executive Function, Adult Version (BRIEF-2A)*. Psychological Assessment Resources.
- Owen, A.M. et al. (1990). *Planning and spatial working memory: a positron emission tomography study in humans*. European Journal of Neuroscience. (CANTAB SWM)
- Binz, M. & Schulz, E. (2023). *Using cognitive psychology to understand GPT-3*. PNAS.
- Cognitive Control in Vision-Language Models (arXiv, 2025). https://arxiv.org/html/2505.18969v1
- Triangulating LLM Progress — Findings EMNLP 2025. https://aclanthology.org/2025.findings-emnlp.1092.pdf
- Deficient Executive Control in Transformer Attention (bioRxiv, 2025). https://www.biorxiv.org/content/10.1101/2025.01.22.634394v2.full.pdf

---

*ExProf-Bench v1.0 — Gerlyn Eduardo Duarte*
*Calibrated with: BADS (Wilson et al., 1996) · BRIEF-2A adult norms n = 1,637 (Gioia et al.) · CANTAB SWM (Owen et al., 1990)*
