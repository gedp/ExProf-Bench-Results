# ExProf-Bench-Results
<img src="https://r2cdn.perplexity.ai/pplx-full-logo-primary-dark%402x.png" style="height:64px;margin-right:32px"/>

# ExProf-Bench: Systematic Assessment of Executive Control in LLMs

**Track:** Executive Functions | **Hackathon:** Measuring Progress Toward AGI (Kaggle × Google DeepMind)
**6 tasks · 150 items · 100% deterministic Python evaluators · Kaggle SDK compatible · 33 models evaluated**

***

## 1. Theoretical Framework

### The Gap We Measure

ExProf-Bench measures *how* a model orchestrates cognition under competing constraints, not what it knows. Autoregressive architectures excel at crystallized knowledge retrieval but fail consistently on tasks demanding fluid executive control (LeCun, 2022).

**Three independent lines of evidence:**

- **de Langis et al. (EACL 2026)** — *"Strong Memory, Weak Control"*: memory/control dissociation in 7 LLMs
- **Song et al. (EMNLP Findings 2024)**: perseveration (A-not-B errors) in rule-shift contexts
- **Upadhayay et al. (ICLR 2025)**: working memory failures under dual-task load


### Clinical Anchoring (Key Differentiator)

ExProf-Bench is structured around the **Unity-and-Diversity model** (Miyake et al., 2000) with normative references from validated clinical instruments:


| Instrument | n | Role | Why it differentiates |
| :-- | :-- | :-- | :-- |
| **BADS** (Wilson et al., 1996) | Clinical validation | T1,T2,T3,T4 structural basis | **No other track benchmark cites BADS** |
| **BRIEF-2A** (PAR Inc., 2024) | 1,637 adults (18-99) | Performance baseline | **Real normative data, not generic "humans"** |

> **Methodological note**: No diagnostic equivalence claimed. BADS/BRIEF-2A operationalize EF dimensions where LLMs fail empirically (de Langis 2026).

***

## 2. The Six Tasks: Dissociable EF Dimensions

| Task | Name | Primary EF | Clinical Basis | Failure Mode |
| :-- | :-- | :-- | :-- | :-- |
| **T1** | RuleShift | Inhibition | BADS Rule Shift Cards | Perseveration |
| **T2** | ZooMap | Planning | BADS Zoo Map Test | Greedy choices |
| **T3** | SixElements | Prospective memory | BADS Six Elements | Task monopolization |
| **T4** | SystSearch | Monitoring | BADS Key Search | Coverage neglect |
| **T5** | TrailBench | Flexibility | Trail Making B | Set collapse |
| **T6** | MemEsp-Dual | Working memory | CANTAB-SWM | Dual-task failure |

### Neuropsychological Distinctions

**T1 vs T5**: T1 = abandon active set (inhibition). T5 = maintain both sets simultaneously (shifting). Factorially distinct (Miyake r≈0.43).

**T5 vs T6**: T5 = phonological loop + central executive. T6 = visuospatial sketchpad + arithmetic (Baddeley 2000).

***

## 3. Evaluator Design (Technical Differentiators)

1. **100% deterministic** — Python vs ground truth. No LLM judges.
2. **Rule 0: Self-correction penalized** — first committed response only (clinical standard).
3. **Cross-load architecture** — every task embeds secondary EF demands.
4. **Axis decomposition** — partial scores per cognitive dimension.

### T2 ZooMap Example (17 trap codes)

| EF Dimension | Traps | BRIEF-2A Analogue |
| :-- | :-- | :-- |
| Look-ahead | `LOOKAHEAD_BOTTLENECK` | Plan/Organize |
| Inhibition | `INHIBITORY_DEADEND` | Inhibit |
| Working Memory | `WM_OVERLOAD` | Working Memory |

Evaluator: BFS-optimal route verification → 0.0-1.0 continuous score.

***

## 4. Executive Profile Index (EPI)

```
EPI = [TEI + PV + (1-TSO) + (1-IS) + TVR + (ER+(1-PD))/2] / 6
```

**EPI = 0** → perfect. **EPI = 1** → total failure.
**BRIEF-2A reference**: Healthy adults EPI < 0.20.

***

## 5. Results (33 Models Evaluated)

### Global Leaderboard

**Top performers**: Gemini-3.1-Pro (0.976), Gemma-4-31B (0.976)
**Bottom**: Gemma-3-1B (0.253)

### Discriminative Power by Task (Std. Dev.)

| Task | Mean | Range | Std.Dev | Status |
| :-- | :-- | :-- | :-- | :-- |
| **T5 Flexibility** | 0.505 | **0.0→1.0** | **0.407** | ⭐ Strongest discriminator |
| T3 Prospective Mem | 0.889 | 0.0→1.0 | 0.252 | High variance |
| T1 Inhibition | 0.731 | 0.0→1.0 | 0.196 | Moderate |
| T6 Working Memory | 0.853 | 0.12→1.0 | 0.201 | Moderate |
| T4 Monitoring | 0.942 | 0.0→1.0 | 0.193 | Easy for frontier |
| T2 Planning | 0.878 | 0.37→1.0 | **0.149** | Easiest |

### Key Empirical Finding: Jagged Frontier

**T5 TrailBench reveals discontinuous performance:**

```
Perfect (1.0): Gemini-3.1-Pro, Gemma-4-31B, Claude-Sonnet-4 (×8)
Collapse: GPT-OSS-120B = 0.40 (vs GPT-OSS-20B = 0.95!)
Bottom: 0.0-0.25 (10+ models)
```

**Parameter count ≠ EF capacity**: GPT-OSS-120B < GPT-OSS-20B on T5.

### Task Heatmap

**Pattern**: Frontier saturates T2/T4. T5 reveals true executive control ceiling.

***

## 6. Kaggle Submission Context

The submitted writeup was condensed under extreme deadline pressure (~30s remaining). This repo contains:

- ✅ Complete BADS/BRIEF-2A justification
- ✅ Full EPI derivation
- ✅ 33-model leaderboard (not 21 as in draft)
- ✅ T5 bimodal discontinuity finding
- ✅ GPT-120B vs 20B counterexample

***

## 7. Code Structure

```
├── evaluators/           # Deterministic Python (recommended: T5+T2+T1)
├── results/             # CSV + plots
└── README.md           # This document
```

**Priority for code upload**: T5 (discriminator) → T2 (planning baseline) → T1 (inhibition).

***

## 8. References

- Miyake et al. (2000). *Unity and Diversity of Executive Functions.* Cognitive Psychology.
- Wilson et al. (1996). *BADS: Behavioural Assessment of Dysexecutive Syndrome.*
- de Langis et al. (2026). *Strong Memory, Weak Control.* EACL 2026.
- PAR Inc. (2024). *BRIEF-2A* (n=1,637 adults).
- LeCun (2022). *Path Toward Autonomous Machine Intelligence.*

***

**Repository serves as complete technical appendix to Kaggle submission \#ExProf-Bench.**

