<div align="center">
  <h1>Probabilities of Allen Interval Relations</h1>
  <p>
    <a href="LICENSE"><img src="https://img.shields.io/badge/License-MIT-yellow.svg" alt="MIT License"></a>&#8201;
    <a href="https://www.python.org/downloads/release/python-396/"><img src="https://img.shields.io/badge/Python-3.9-blue.svg" alt="Python 3.9"></a>&#8201;
    <a href="https://github.com/vxrdis/allen-interval-probabilities/commits/main"><img src="https://img.shields.io/github/last-commit/vxrdis/allen-interval-probabilities" alt="Last Commit"></a>&#8201;
    <a href="https://github.com/vxrdis/allen-interval-probabilities"><img src="https://img.shields.io/github/repo-size/vxrdis/allen-interval-probabilities" alt="Repo Size"></a>&#8201;
    <a href="https://black.readthedocs.io/en/stable/"><img src="https://img.shields.io/badge/code%20style-black-000000.svg" alt="Code Style: Black"></a>
  </p>
  <p>
    <a href="https://www.tcd.ie/" target="_blank" rel="noopener noreferrer">
      <picture>
        <source media="(prefers-color-scheme: dark)" srcset="https://www.tcd.ie/identity/assets/logos/Logos%20page/png/Trinity%20logo%20%E2%80%93%20White.png">
        <source media="(prefers-color-scheme: light)" srcset="https://www.tcd.ie/identity/assets/logos/Logos%20page/jpg/Trinity_Main_Logo.jpg">
        <img src="https://www.tcd.ie/identity/assets/logos/Logos%20page/jpg/Trinity_Main_Logo.jpg" alt="Trinity College Dublin Logo" width="300" loading="lazy" decoding="async">
      </picture>
    </a>
  </p>
  <p>
    A <a href="https://projects.scss.tcd.ie" target="_blank" rel="noopener noreferrer">Final Year Project</a> by <strong>Cillín Forrester</strong><br>
    under the supervision of Dr <a href="https://www.scss.tcd.ie/Tim.Fernando/" target="_blank" rel="noopener noreferrer">Tim Fernando</a><br>
    submitted to the <a href="https://www.tcd.ie/scss/" target="_blank" rel="noopener noreferrer">School of Computer Science and Statistics</a><br>
    in partial fulfilment of the requirements for the degree of<br>
    B.A. (Mod.) in <a href="https://www.tcd.ie/scss/courses/undergraduate/computer-science-linguistics-and-a-language/" target="_blank" rel="noopener noreferrer">Computer Science, Linguistics and a Language</a>
  </p>
</div>

## Contents

- [Project Overview](#project-overview)
- [Theoretical Motivation](#theoretical-motivation-and-context)
- [Literature Review](#literature-review-and-related-work)
- [Research Objectives](#research-objectives)
- [Project Structure](#project-structure-and-contents)
- [Usage Instructions](#usage-instructions)
- [Hypotheses and Evaluations](#hypotheses-and-evaluations)
- [Visualisation](#visualisation-and-interaction)
- [Future Work](#future-work)
- [Citation](#citation)
- [References](#references)

---

This repository presents a **Final Year Project** investigating probabilistic extensions of Allen's Interval Algebra (a framework that defines 13 possible relationships between time intervals). It evaluates key hypotheses about interval relations using empirical simulation, statistical testing, and interactive visualisation.

The project integrates **formal temporal logic** (a system for reasoning about time using logical rules) with **stochastic modelling** (mathematical techniques for analysing random processes), offering an extensible framework for reasoning about time under uncertainty.

## Project Overview

**Allen's Interval Algebra** classifies temporal relations between intervals into 13 mutually exclusive categories. While this framework captures qualitative structure, it makes no assumptions about the relative likelihood of each relation.

This project addresses that gap by simulating interval dynamics under various probabilistic assumptions (**birth–death models**, where intervals randomly begin and end according to specified probabilities). It tests the null hypothesis of a uniform distribution across relations and explores how **composition tables** behave in practice — including **entropy**, **skew**, and hypothesis alignment.

Key aims include:

- Simulating interval systems to empirically estimate the probability of each of Allen's relations
- Testing the **Principle of Indifference** and comparing to predictions from Suliman and Fernando–Vogel
- Mapping the structure of the composition table through **probabilistic chaining**
- Building an interactive dashboard for exploring simulation results

## Theoretical Motivation and Context

**Allen's Interval Algebra** provides a deterministic framework for reasoning about temporal relations between intervals. However, this classical approach faces fundamental limitations when applied to real-world scenarios where uncertainty is inevitable.

Deterministic temporal reasoning cannot adequately address:

1. **Inherent uncertainty** in establishing precise temporal boundaries
2. **Measurement imprecision** when determining interval endpoints
3. **Incomplete knowledge** about temporal sequences
4. **Varying degrees of confidence** in temporal assertions
5. **Decision-making under uncertainty** requiring probabilistic reasoning

When modelling cognitive processes, natural language understanding, or real-time systems, these limitations become critical barriers.

> A probabilistic extension of Allen's algebra allows for reasoning that accommodates uncertainty, enables robust inference from noisy data, and better reflects how humans actually reason about temporal relations.

This project specifically addresses this gap by developing an empirical foundation for probabilistic temporal reasoning that preserves the logical structure of Allen's framework while embracing uncertainty.

## Research Objectives

This project seeks to answer the following questions:

- Determine how the probabilities of Allen's interval relations vary under different **stochastic assumptions** (e.g., birth/death rates)
- Assess whether **empirical distributions** significantly differ from a uniform distribution (Principle of Indifference)
- Investigate how varying simulation parameters impact the composition and resultant probability distributions of interval chains
- Develop clear, interactive visualisations and statistical analyses to facilitate deeper insights into temporal structure

## Project Structure and Contents

This repository is structured to clearly delineate between core simulations, analysis tools, and documentation:

<pre>
allen-interval-probabilities/
├── <a href="./docs/">docs/</a>
├── <a href="./batch_runner.py">batch_runner.py</a>
├── <a href="./composition_runner.py">composition_runner.py</a>
├── <a href="./simulations.py">simulations.py</a>
├── <a href="./intervals.py">intervals.py</a>
├── <a href="./relations.py">relations.py</a>
├── <a href="./constants.py">constants.py</a>
├── <a href="./stats.py">stats.py</a>
├── <a href="./report_generator.py">report_generator.py</a>
├── <a href="./RESULTS.md">RESULTS.md</a>
└── <a href="./requirements.txt">requirements.txt</a>
</pre>

## Usage Instructions

### Installation

Clone the repository and install dependencies:

```bash
git clone https://github.com/vxrdis/allen-interval-probabilities
cd allen-interval-probabilities
pip install -r requirements.txt
```

### Running Simulations

Simulate basic interval relations empirically by running:

```bash
python batch_runner.py
```

For advanced interval composition simulations (exploring how Allen relations chain together), use:

```bash
python composition_runner.py --trials 500
```

This will systematically generate all 169 possible relation pairs (13×13) and collect statistics on their compositions.

### Generating Reports

To automatically generate an updated project report (in Markdown format), execute:

```bash
python report_generator.py
```

---

## Literature Review and Related Work

**Allen's Interval Algebra**, first formalised by [James F. Allen (1983)](https://doi.org/10.1145/182.358434), provides a framework of 13 qualitative relations — such as before, meets, overlaps, and their inverses — to describe how time intervals relate.

Although widely adopted in fields like computational linguistics, artificial intelligence, and temporal logic, the original deterministic formulation does not inherently handle uncertainty or probabilistic scenarios that occur naturally in real-world temporal data.

### Probabilistic Extensions

Recent research has explored probabilistic extensions of Allen's relations:

- [Fernando and Vogel (2019)](https://www.scss.tcd.ie/Tim.Fernando/NLPinAI_2019.pdf) challenged the assumption of uniform distribution among Allen's relations
- They demonstrated analytically that certain temporal relations (particularly those without endpoint coincidences) inherently occur more frequently under random conditions
- Their **finite-order model** predicts that as timelines become denser, exact endpoint coincidences approach zero probability
- Specifically, under asymptotic conditions where both birth and death probabilities approach zero (`p → 0`, `q → 0`), their model predicts domination by six "long-range" relations

#### Suliman's Prediction

> Suliman proposed that seven relations (equals, before, after, starts, started_by, meets, met_by) occur with probability 1/9, and the remaining six with 1/27.

At precisely balanced birth-death probabilities (`p = 0.5` and `q = 0.5`), the empirical distribution closely matches this model (χ² p ≈ 0.76), offering strong support for Suliman's prediction. This balanced condition (equal probability of intervals starting and ending) creates the specific stochastic environment where Suliman's 1/9 vs 1/27 distribution holds.

Outside this balanced region, Suliman's model is rejected — suggesting its validity depends on specific temporal density regimes.

#### Fernando–Vogel Asymptotic Model

> Fernando and Vogel predicted that as `p → 0` and `q → 0` (extremely low probabilities of birth and death), six long-range relations (before, after, during, contains, overlaps, overlapped_by) should dominate, each converging to a probability of ~1/6.

This pattern emerges clearly in simulations at extreme low `p` and `q`, supporting their **asymptotic argument** for sparse timelines.

### Complementary Frameworks

Complementary approaches have appeared in temporal reasoning frameworks and NLP:

- [Santos and Young's (1999)](<https://doi.org/10.1016/S0888-613X(99)00009-2>) **Probabilistic Temporal Networks** combined Bayesian methods with interval-based constraints
- [Badaloni and Giacomin (2006)](https://doi.org/10.1016/j.artint.2006.04.001) _A fuzzy extension of Allen's interval algebra_. _Artificial Intelligence_, 170(10), 872–908.

### Statistical Validation

Beyond theoretical and simulation frameworks, statistical analyses have been critical for validating these probabilistic models:

- Metrics such as **entropy** quantify the uncertainty inherent in relation distributions
- **Chi-square goodness-of-fit** tests have evaluated model accuracy
- Real-world datasets confirm theoretical biases — relations like "before" dominate naturally occurring timelines

### Practical Applications

Practical applications of probabilistic Allen algebra are increasingly significant:

- **Temporal annotation standards** like [TimeML](https://timeml.github.io/) leverage these relations
- In archaeology, tools like [ArchaeoPhases](https://archaeostat.github.io/ArchaeoPhases/) use Allen's relations probabilistically to quantify uncertainty in chronological intervals

However, despite the depth of theoretical exploration, practical tools and visualisation dashboards for probabilistic Allen relations have remained limited.

> This project addresses this gap directly through interactive visualisations, allowing intuitive exploration of relation probabilities, parameter sensitivity, entropy dynamics, and three-interval composition scenarios.

This literature review highlights important research gaps that the current project aims to address: dynamically derived relation probabilities, comprehensive probabilistic composition tables, deeper empirical validation, and integrated interactive tools.

## Documentation and Project Reports

Detailed documentation relevant to this project can be found in the `docs/` directory, structured to clearly separate project-specific documents from foundational literature.

### Project Documents (`docs/`)

- [`FYP-Interim-Report.pdf`](./docs/FYP-Interim-Report.pdf)
  Interim report detailing project rationale, methodologies, initial findings, and work completed.

- [`Trinity-GenAI-Guidelines.pdf`](./docs/Trinity-GenAI-Guidelines.pdf)
  Official Trinity College Dublin guidelines on using generative AI tools in academic projects.

- [`allen-intervals-automata.pdf`](./docs/allen-intervals-automata.pdf)
  Diagrams illustrating finite-state automata representations of interval relations.

- [`finite-string-definitions.pdf`](./docs/finite-string-definitions.pdf)
  Formal definitions underpinning finite temporality and symbolic manipulation of interval events.

- [`suliman-model-summary.pdf`](./docs/related-work/suliman-model-summary.pdf)
  A concise summary providing context for foundational concepts used in interval simulations.

- [`suliman-transition-probabilities.pdf`](./docs/suliman-transition-probabilities.pdf)
  Transition probability matrices providing theoretical validation for simulation parameters.

### Related Work and Background Literature (`docs/related-work/`)

- [`Allen1983-IntervalAlgebra.pdf`](./docs/related-work/Allen1983-IntervalAlgebra.pdf)
  James Allen's foundational 1983 paper that originally defined the interval algebra and introduced the 13 interval relations.

- [`Alspaugh-AllenIntervalAlgebraNotes.pdf`](./docs/related-work/Alspaugh-AllenIntervalAlgebraNotes.pdf)
  Annotated explanations and detailed interpretations of Allen's interval algebra concepts by Thomas Alspaugh.
  **Attribution**: Thomas A. Alspaugh, _Allen's Interval Algebra_, https://thomasalspaugh.org/pub/fnd/allen.html.
  Licensed under [Creative Commons BY-NC-SA](https://creativecommons.org/licenses/by-nc-sa/4.0/).

- [`Mahowald2024-DissociatingLanguageThought-LLMs.pdf`](./docs/related-work/Mahowald2024-DissociatingLanguageThought-LLMs.pdf)
  Cognitive science research clarifying the limitations of language-based AI models in handling reasoning tasks such as temporal reasoning, motivating symbolic probabilistic approaches.

- [`Petrukhin2024-TimelineGranularity-FSM.pdf`](./docs/related-work/Petrukhin2024-TimelineGranularity-FSM.pdf)
  Recent MCS dissertation extending interval algebra to finite-state machine representations with explicit timeline granularity.

- [`Suliman2021-FiniteTemporality-Thesis.pdf`](./docs/related-work/Suliman2021-FiniteTemporality-Thesis.pdf)
  Prior academic work which introduced stochastic methods in finite temporality contexts.

- [`fernando-vogel-allen-priors.pdf`](./docs/related-work/fernando-vogel-allen-priors.pdf)
  Analytical derivations of theoretical priors for interval relation probabilities.

- [`jurafsky-martin-ch19-temporal.pdf`](./docs/related-work/jurafsky-martin-ch19-temporal.pdf)
  Chapter from Jurafsky & Martin's textbook providing broader NLP context for temporal information extraction.

---

## Hypotheses and Evaluations

This project empirically tests two central hypotheses through controlled stochastic simulations.

### 1. Probability Distribution of Interval Relations

- **Null Hypothesis:** Each of Allen's 13 interval relations is equally likely to occur (uniform distribution: 1/13).

- **Method:**

  - Thousands of simulations were run with varying **birth** (`pBorn`) and **death** (`pDie`) probabilities
  - Relation counts were aggregated and normalised to estimate empirical distributions

- **Result:** The null hypothesis is consistently refuted across all parameter sets.

  - In every case, certain relations (e.g. `before`, `meets`) dominate while others (e.g. `equal`) are rare
  - This demonstrates significant and robust deviation from the theoretical uniform baseline

- **Statistical Evidence:**
  - **Entropy** varies substantially across parameter sets
  - **Chi-squared tests** consistently return p-values < 0.05
  - These confirm strong non-uniformity with high confidence

#### Suliman's Prediction

> Suliman proposed that seven relations (equals, before, after, starts, started_by, meets, met_by) occur with probability 1/9, and the remaining six with 1/27.

At `p = 0.5` and `q = 0.5`, the empirical distribution closely matches this model (χ² p ≈ 0.76), offering strong support for Suliman under balanced conditions.

Outside this region, Suliman's model is rejected — suggesting its validity depends on specific temporal density regimes.

#### Fernando–Vogel Asymptotic Model

> Fernando and Vogel predicted that as `p → 0` and `q → 0`, six long-range relations (before, after, during, contains, overlaps, overlapped_by) should dominate, each converging to a probability of ~1/6.

This pattern emerges clearly in simulations at extreme low `p` and `q`, supporting their **asymptotic argument** for sparse timelines.

#### Entropy and Skew

- Entropy is maximised when `p` and `q` are moderate (e.g. 0.5)
- Entropy is minimised when intervals are short and rare
- The **PMS/OD ratio** (precedes, meets, starts vs. overlaps, during) grows extremely large in sparse regimes — e.g. over 2000×
- This confirms strong structural skew in relation types when intervals are brief or rarely instantiated

### 2. Composition Table Probabilities

- **Null Hypothesis:** All entries in Allen's interval composition table are equally probable under random chains (e.g. xRy ∧ yRz ⇒ x?z).

- **Planned Method:**

  - Simulations of triple-interval chains will estimate the frequency of inferred compositions
  - For each pair of input relations (r1, r2), we will track the empirical distribution over resulting compositions r3

- **Goal:** To map the structure of empirical compositions across the full transitivity space.
  - This will allow us to evaluate how composition outcomes vary with birth and death probabilities
  - We can determine whether the table exhibits systematic skew or asymmetry

---

## Visualisation and Interaction

To effectively communicate findings, **interactive visualisations** using Dash and Plotly are integrated, allowing intuitive exploration of interval relation probabilities and compositional logic.

The visualisation components clearly illustrate:

- Deviations from theoretical expectations
- Dynamic investigation of parameter effects (like `pBorn` and `pDie`)
- Probability distributions under varying conditions

For detailed visualisation results and extensive discussion, please refer to the comprehensive `RESULTS.md`.

---

## Future Work

Planned extensions over the coming days include:

### Entropy and Information-Theoretic Analysis

- Integration of **entropy measures** to quantify the uncertainty in observed distributions
- Comparisons against baseline distributions (e.g., uniform, theoretical priors)
- Where appropriate, **KL divergence** may also be explored

### Probabilistic Composition Mining

- Extending simulations to estimate the empirical probabilities of inferred relations
- Analysing how compositions vary under different stochastic assumptions
- Mapping **probability flows** through composition chains

### Visualisation Enhancements

- Adding summary plots (bar graphs, heatmaps) to illustrate frequency across simulation runs
- Developing **interactive dashboards** for exploring parameter spaces
- Creating comparative visualisations of theoretical vs. empirical distributions

### Statistical Evaluation

- Introducing statistical tests (chi-squared, divergence measures)
- Assessing how closely empirical results match or deviate from theoretical expectations
- Conducting **sensitivity analyses** to identify critical parameters

---

## Citation

If you reference or build upon this work, please cite:

> **Cillín Forrester**, _Probabilities of Allen Interval Relations_.
> Final Year Project, B.A. (Mod.) in Computer Science, Linguistics and a Language.
> Trinity College Dublin, The University of Dublin (2025).
> [https://github.com/vxrdis/allen-interval-probabilities](https://github.com/vxrdis/allen-interval-probabilities)

```bibtex
@misc{forrester2025allen,
  author       = {Cillín Forrester},
  title        = {Probabilities of Allen Interval Relations},
  year         = {2025},
  institution  = {Trinity College Dublin, The University of Dublin},
  howpublished = {\url{https://github.com/vxrdis/allen-interval-probabilities}},
  note         = {Final Year Project (B.A. (Mod.) in Computer Science, Linguistics and a Language)}
}
```

---

## References

- **Allen, J.F.** (1983). _Maintaining Knowledge about Temporal Intervals_. _Communications of the ACM_, 26(11), 832–843. [DOI:10.1145/182.358434](https://doi.org/10.1145/182.358434).

- **Alspaugh, T.A.** (2019). _Allen's Interval Algebra_. Retrieved from [thomasalspaugh.org](https://thomasalspaugh.org/pub/fnd/allen.html).

- **Badaloni, S., & Giacomin, M.** (2006). _A fuzzy extension of Allen's interval algebra_. _Artificial Intelligence_, 170(10), 872–908. [DOI:10.1016/j.artint.2006.04.001](https://doi.org/10.1016/j.artint.2006.04.001).

- **Fernando, T., & Vogel, C.** (2019). _Prior Probabilities of Allen Interval Relations over Finite Orders_. In _Proceedings of the NLPinAI Workshop_, part of the 11th International Conference on Agents and Artificial Intelligence (ICAART 2019), Prague, Czech Republic. [PDF](https://www.scss.tcd.ie/Tim.Fernando/NLPinAI_2019.pdf).

- **Jurafsky, D., & Martin, J.H.** (2025). _Speech and Language Processing: An Introduction to Natural Language Processing, Computational Linguistics, and Speech Recognition with Language Models_ (3rd ed., draft). Chapter 20: Information Extraction — Relations, Events, and Time. Retrieved from [web.stanford.edu/~jurafsky/slp3](https://web.stanford.edu/~jurafsky/slp3/).

- **Mahowald, K., Ivanova, A., Kean, H., Thompson, B., Gibson, E., & Fedorenko, E.** (2024). _Dissociating language and thought in large language models_. _Trends in Cognitive Sciences_, 28(4), 319–334. [DOI:10.1016/j.tics.2024.01.011](https://doi.org/10.1016/j.tics.2024.01.011).

- **Petridis, S., Paliouras, G., & Perantonis, S.J.** (2010). _Allen's hourglass: Probabilistic treatment of interval relations_. NCSR "Demokritos", Greece. [PDF](https://citeseerx.ist.psu.edu/document?repid=rep1&type=pdf&doi=85b2f290ed665bd0e8844f75322885ad0aa037cb).

- **Petrukhin, P.** (2024). _FSMs and Timeline Granularity in Interval Reasoning_. MCS Dissertation, Trinity College Dublin. [PDF](https://publications.scss.tcd.ie/theses/diss/2024/TCD-SCSS-DISSERTATION-2024-024.pdf).

- **Santos, P., & Young, R.** (1999). _Probabilistic temporal networks: A unified framework for reasoning with time and uncertainty_. _International Journal of Approximate Reasoning_, 20(3), 263–291. [DOI:10.1016/S0888-613X(99)00009-2](<https://doi.org/10.1016/S0888-613X(99)00009-2>).

- **Suliman, A.** (2021). _Finite Temporality: A Probabilistic Approach to Interval Relations_. Undergraduate Thesis, Trinity College Dublin. [PDF](https://www.scss.tcd.ie/~sulimanm/assets/thesis.pdf).
