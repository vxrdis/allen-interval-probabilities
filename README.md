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

## Project Structure

- `constants.py` – Allen relation and state definitions
- `relations.py` – Allen relations and composition logic
- `intervals.py` – Interval generation and relation detection
- `simulations.py` – Birth/death process simulation engine
- `stats.py` – Statistical analysis and hypothesis testing
- `README.md` – Project description
- `LICENSE` – MIT License

## Usage

The project provides multiple ways to simulate and analyze interval relations:

1. Use `intervals.py` functions to generate random intervals and determine their relations:
   - `gen()` - Generate single intervals with birth/death probabilities
   - `run()` - Generate two intervals and determine their relation
   - `many()` - Run multiple simulations with identical parameters

2. Use `simulations.py` for more complex state transition simulations:
   - `arSimulate()` - Run birth/death process simulations
   - `demo()` - Run a series of simulations with different parameters

3. Use `stats.py` to analyze relation distributions:
   - `entropy()` - Calculate information entropy
   - `chi_square_uniform()` - Test against uniform distribution
   - `describe()` - Get comprehensive statistics