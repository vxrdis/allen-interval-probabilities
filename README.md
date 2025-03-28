# Probabilities of Allen Interval Relations

Final Year Project — B.A. (Mod.) in Computer Science, Linguistics and a Language

Trinity College Dublin

## Overview

This project extends Allen's Interval Algebra (1983) by introducing probabilistic modeling and simulations to handle uncertainty in temporal relations and their composition.

## Features

- Implementation of the 13 Allen interval relations
- Composition (transitivity) table logic
- Probabilistic birth/death state transition simulations
- Interval generation with customizable parameters
- Statistical analysis and hypothesis testing
- Multiple simulation modes with varying parameters
- Batch simulation processing
- Automated report generation

## Installation

To install the required dependencies:

```bash
pip install -r requirements.txt
```

## Project Structure

- `constants.py` – Allen relation and state definitions
- `relations.py` – Allen relations and composition logic
- `intervals.py` – Interval generation and relation detection
- `simulations.py` – Birth/death process simulation engine
- `stats.py` – Statistical analysis and hypothesis testing
- `batch_runner.py` – Run multiple simulations with various parameters
- `report_generator.py` – Generate Markdown reports from simulation results
- `requirements.txt` – Python dependencies
- `README.md` – Project description
- `LICENSE` – MIT License

## Usage

The project provides multiple ways to simulate and analyze interval relations:

1. Use `intervals.py` functions to generate random intervals and determine their relations:
   - `gen()` - Generate single intervals with birth/death probabilities
   - `run()` - Generate two intervals and determine their relation
   - `many()` - Run multiple simulations with identical parameters
   - `simulate_relations()` - Generate intervals with different parameters for each interval

2. Use `simulations.py` for more complex state transition simulations:
   - `arSimulate()` - Run birth/death process simulations
   - `demo()` - Run a series of simulations with different parameters

3. Use `stats.py` to analyze relation distributions:
   - `entropy()` - Calculate information entropy
   - `chi_square_uniform()` - Test against uniform distribution
   - `chi_square_against_theory()` - Compare against theoretical distributions
   - `describe()` - Get comprehensive statistics

4. Use `batch_runner.py` to run large-scale simulations:
   - Automatically runs simulations with various probability combinations
   - Saves results to a JSON file for further analysis

5. Use `report_generator.py` to create reports:
   - Generates a Markdown table summarizing simulation results
   - Includes entropy, ratio statistics, and chi-square tests against different distributions

## Workflow

1. Run batch simulations: `python batch_runner.py`
2. Generate a summary report: `python report_generator.py`
3. View the results in the generated `REPORT.md` file