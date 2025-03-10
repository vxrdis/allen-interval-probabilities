# Probabilities of Allen Interval Relations

Final Year Project — B.A. (Mod.) in Computer Science, Linguistics and a Language

Trinity College Dublin

---

## Overview

This project extends James F. Allen's Interval Algebra (1983) by introducing probabilistic modelling to temporal reasoning. Allen's original framework defines 13 distinct relations between time intervals (before, meets, overlaps, etc.) and a composition table for transitivity reasoning, but does not address uncertainty or probabilistic scenarios.

By implementing birth/death probabilistic automata, this project quantifies the likelihood of different interval relations emerging under various parameters, offering insights into how temporal reasoning operates under uncertainty. The work bridges theoretical temporal logic with practical computational applications through simulation and interactive visualisation.

### Limitations of Large Language Models (LLMs)

While LLMs excel at language-related tasks, they struggle with deeper cognitive functions such as temporal reasoning—a limitation highlighted in recent research on "Dissociating language and thought" (2024). This project addresses this gap by focusing on probabilistic temporal reasoning, which is beyond the current capabilities of LLMs.

---

## Key Features

- **Complete Allen Interval Implementation**: All 13 basic relations (before, meets, overlaps, starts, during, finishes, equals, and their inverses)

- **Compositional Reasoning**: Full composition (transitivity) table generation and analysis

- **Probabilistic Simulations**: Birth/death automata with configurable parameters (pBorn, pDie)

- **Statistical Analysis**:
  - Hypothesis testing for distribution uniformity
  - Convergence pattern analysis under varying parameters
  - Statistical validation of theoretical predictions

- **Interactive Dashboard** with three integrated visualisation components:
  - Animated Distribution Evolution (real-time)
  - Interactive Composition Heatmap
  - Parameter Surface Explorer (3D visualisation)

- **Comparative Analysis** of different parameter configurations and their effect on relation distributions

---

## Visualisations

### Basic Distribution of Allen Relations
![Basic Distribution](./visualisations/basic_distribution.png)

### Composition Table Entropy Analysis
![Composition Entropy](./visualisations/composition_entropy.png)

### Composition Table Size Analysis
![Composition Size](./visualisations/composition_size.png)

---

## Project Structure

```
allen-interval-probabilities/
│
├── relations.py              # Core implementation of Allen's 13 interval relations
├── simulations.py            # Birth/death automata and simulation engine
├── visualisations.py         # Basic visualisation utilities and static charts
│
├── advanced_visualisations.py # Complex visualisation components (3D plots, heatmaps)
├── animated_distribution.py  # Real-time animation of distribution convergence
├── composition_heatmap.py    # Interactive composition table visualisation
├── parameter_surface.py      # 3D surface plots for parameter space exploration
│
├── dashboard_integration.py  # Integration of all visualisation components
├── dashboard_shell.py        # Base framework for the interactive dashboard
├── app.py                    # Main application entry point
│
├── visualisations/           # Static output from simulation runs
│   ├── basic_distribution.png
│   ├── composition_size.png
│   ├── composition_entropy.png
│   └── ...                   # Parameter-specific distribution charts
│
├── requirements.txt          # Project dependencies
├── LICENSE                   # MIT License
└── README.md                 # This file
```

---

## Setup and Usage

### Prerequisites
- Python 3.7+
- pip package manager

### Local Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/vxrdis/allen-interval-probabilities.git
   cd allen-interval-probabilities
   ```

2. Create and activate a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

### Running Simulations

```python
# Example simulation script
from relations import AllenRelation
from simulations import IntervalSimulation

# Configure and run a simulation with 10,000 trials
sim = IntervalSimulation(born_prob=0.1, die_prob=0.1)
results = sim.run_trials(10000)

# Display distribution of relations
distribution = results.get_distribution()
print(distribution)

# Test hypothesis (uniform distribution)
from simulations import test_uniform_hypothesis
p_value = test_uniform_hypothesis(distribution)
print(f"P-value for uniform distribution test: {p_value}")
```

### Testing Hypotheses

```python
# Testing the null hypothesis that Allen relations follow a uniform distribution
from simulations import test_multiple_parameters

# Test across a range of birth/death probabilities
parameter_sets = [
    (0.1, 0.1), (0.2, 0.1), (0.5, 0.5), (0.01, 0.01)
]
results = test_multiple_parameters(parameter_sets, trials=10000)

# All results refute the uniform distribution hypothesis (p < 0.05)
for params, p_value in results:
    print(f"Parameters {params}: p-value = {p_value}")
```

### Running the Dashboard

The interactive dashboard provides a comprehensive interface for exploring all aspects of the project:

```bash
# Start the dashboard server
python app.py
```

Then navigate to `http://127.0.0.1:8050/` in your web browser to access the dashboard.

The dashboard offers:
- Interactive parameter controls (pBorn, pDie)
- Real-time visualisation of simulation results
- Composition table exploration
- 3D parameter surface visualisation
- Hypothesis testing results

---

## Key Findings

Our simulations consistently refute both null hypotheses:

### 1. Allen Relations Distribution

Under various parameter settings, Allen relations do not follow a uniform distribution (1/13 probability each). Instead, different parameter values lead to distinct convergence patterns:
- For p=q→0: Relations "before" and "after" dominate with probability approaching 1/2
- For p=2q→0: Different convergence pattern emerges

### 2. Composition Table Distribution

Entries in the composition table show significant variation in probability, rejecting the null hypothesis of uniform distribution.

These findings highlight how probabilistic constraints shape temporal reasoning, offering insights beyond Allen's original qualitative framework.

---

## Deployment

The dashboard is planned to be deployed on Render for public access at [https://allen-interval-app.onrender.com/](https://allen-interval-app.onrender.com/). Currently, it works on localhost only.

1. Fork this repository to your GitHub account
2. Create a new Web Service on Render
3. Connect your GitHub repository
4. Configure the build:
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `python app.py`
5. Add the environment variable: `PYTHON_VERSION=3.9`

*Note: Deployment is currently under testing. Some features may require additional configuration.*

---

## Credits

This project was developed using:
- Python scientific stack (NumPy, Pandas, SciPy)
- Plotly and Dash for interactive visualisations
- General AI tools were used for development assistance

Special thanks to my supervisor Tim Fernando and the School of Computer Science and Statistics at Trinity College Dublin for supporting this research.

---

## References

- Allen, J. F. (1983). Maintaining knowledge about temporal intervals. Communications of the ACM, 26(11), 832-843.
- "Dissociating language and thought" (2024). Trends in Cognitive Sciences. https://www.sciencedirect.com/science/article/pii/S1364661324000275
- Allen's Interval Algebra: [https://thomasalspaugh.org/pub/fnd/allen.html](https://thomasalspaugh.org/pub/fnd/allen.html)
