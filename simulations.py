"""
Allen's Interval Algebra Simulations

This module implements simulations to study the empirical probabilities of Allen's interval relations
under various birth and death probabilities. The relation codes and ordering follow Thomas Alspaugh's
notation and table (https://thomasalspaugh.org/pub/fnd/allen.html).

The simulation models intervals that transition from 'unborn' (0) to 'alive' (1) to 'dead' (2)
based on probabilistic state transitions. By running many trials, we can observe the natural
frequencies of different interval relationships and test various hypotheses about their distributions.
"""

import random
import numpy as np
import scipy.stats as stats
import matplotlib.pyplot as plt
from relations import (
    list_all_relations,
    compose_relations,
    get_relation_name,
    get_inverse_relation,
    ALLEN_RELATION_ORDER,
)
from shared_utils import normalize_counts

# Global variables
tally = {}  # Parametrized tally with parameter = str(pBorn) + "," + str(pDie)
composition_tally = {}  # For storing composition results


def set_random_seed(seed=42):
    """
    Set the random seed for reproducibility.

    Args:
        seed: Integer seed value for random number generator
    """
    random.seed(seed)
    np.random.seed(seed)


def demo(use_seed=True, trials=10000):
    """
    Run demonstration simulations with various probability settings.

    Args:
        use_seed: If True, use a fixed random seed for reproducibility
        trials: Number of simulation trials to run
    """
    if use_seed:
        set_random_seed()

    print(f"\nRunning simulations with {trials} trials each:")
    print("-" * 60)

    # Run simulations with various probability settings
    configs = [
        (0.5, 0.5),
        (0.1, 0.1),
        (0.01, 0.01),
        (0.001, 0.001),
        (0.2, 0.1),
        (0.02, 0.01),
        (0.002, 0.001),
    ]

    for pBorn, pDie in configs:
        print(f"\nSimulation with pBorn={pBorn}, pDie={pDie}:")
        result = arSimulate(pBorn, pDie, trials)
        print_distribution(result)

        # Test uniform distribution hypothesis
        test_uniform_distribution(result)

    # Generate and display composition table for a specific config
    print("\n" + "=" * 80)
    print("Probabilistic Composition Table (pBorn=0.1, pDie=0.1):")
    print("=" * 80)
    generate_composition_table(0.1, 0.1, 1000)

    # Save results to files
    print("\nUpdated tally and probabilities in file output_simulations.txt")
    ta2file("output_simulations.txt")
    pr2file("output_simulations.txt")
    print("Iterating demo() updates tally and output_simulations.txt")


def arSimulate(probBorn, probDie, trials):
    """
    Run Allen relation simulation with specified birth/death probabilities.

    Args:
        probBorn: Probability of transition from unborn to alive
        probDie: Probability of transition from alive to dead
        trials: Number of trials to run

    Returns:
        Dictionary of relation frequencies
    """
    redRuns = simulateRed(probBorn, probDie, trials)
    dic = scoreRed(redRuns)
    p = probDic(dic, trials)
    updateTally(probBorn, probDie, dic)
    return dic


def simulateRed(pBorn, pDie, trials):
    """
    Simulate interval state transitions and produce histories.

    This function simulates multiple trials of two intervals transitioning from:
    - state 0 (unborn)
    - to state 1 (alive)
    - to state 2 (dead)

    Args:
        pBorn: Probability of transition from unborn to alive
        pDie: Probability of transition from alive to dead
        trials: Number of trials to run

    Returns:
        List of histories (state transitions)
    """
    temp = []
    for run in range(trials):
        hist = [[0, 0]]  # Both intervals start as unborn [a-state, b-state]

        # Continue until both intervals are dead
        while not (hist[-1] == [2, 2]):
            first = updateState(hist[-1][0], pBorn, pDie)
            second = updateState(hist[-1][1], pBorn, pDie)

            # Only append if state changed (avoid duplication)
            if not (hist[-1] == [first, second]):
                hist.append([first, second])

        temp.append(hist)
    return temp


def updateState(state, pBorn, pDie):
    """
    Update the state of an interval based on transition probabilities.

    Args:
        state: Current state (0=unborn, 1=alive, 2=dead)
        pBorn: Probability of transition from unborn to alive
        pDie: Probability of transition from alive to dead

    Returns:
        New state
    """
    toss = random.random()
    if state == 0 and toss < pBorn:
        return 1  # Transition from unborn to alive
    elif state == 1 and toss < pDie:
        return 2  # Transition from alive to dead
    else:
        return state  # No change


def scoreRed(reducedRuns):
    """
    Score the reduced runs to count occurrences of each Allen relation.

    Args:
        reducedRuns: List of histories (state transitions)

    Returns:
        Dictionary counting occurrences of each relation
    """
    dic = arInitDic()
    for r in reducedRuns:
        relation_code = arCode(r)
        if relation_code:  # Only count if valid relation is identified
            dic[relation_code] += 1
    return dic


def arCode(Hist):
    """
    Identify the Allen relation corresponding to a history of state transitions.

    This function maps interval transition histories to Alspaugh's Allen relation codes.

    Args:
        Hist: History of state transitions

    Returns:
        Allen relation code or None if no match
    """
    # Map histories to Allen relation codes using Alspaugh's notation
    if Hist == [[0, 0], [1, 1], [2, 2]]:
        return "e"  # Equal (was 'eq')
    elif Hist == [[0, 0], [1, 0], [2, 0], [2, 1], [2, 2]]:
        return "p"  # Before/Precedes (was 'b')
    elif Hist == [[0, 0], [0, 1], [0, 2], [1, 2], [2, 2]]:
        return "P"  # After (was 'bi')
    elif Hist == [[0, 0], [1, 0], [1, 1], [2, 1], [2, 2]]:
        return "o"  # Overlaps (same code)
    elif Hist == [[0, 0], [0, 1], [1, 1], [1, 2], [2, 2]]:
        return "O"  # Overlapped-by (was 'oi')
    elif Hist == [[0, 0], [1, 0], [2, 1], [2, 2]]:
        return "m"  # Meets (same code)
    elif Hist == [[0, 0], [0, 1], [1, 2], [2, 2]]:
        return "M"  # Met-by (was 'mi')
    elif Hist == [[0, 0], [0, 1], [1, 1], [2, 1], [2, 2]]:
        return "d"  # During (same code)
    elif Hist == [[0, 0], [1, 0], [1, 1], [1, 2], [2, 2]]:
        return "D"  # Contains (was 'di')
    elif Hist == [[0, 0], [1, 1], [2, 1], [2, 2]]:
        return "s"  # Starts (same code)
    elif Hist == [[0, 0], [1, 1], [1, 2], [2, 2]]:
        return "S"  # Started-by (was 'si')
    elif Hist == [[0, 0], [0, 1], [1, 1], [2, 2]]:
        return "f"  # Finishes (same code)
    elif Hist == [[0, 0], [1, 0], [1, 1], [2, 2]]:
        return "F"  # Finished-by (was 'fi')
    return None  # No match


def arInitDic():
    """
    Initialize dictionary with all Allen relations set to zero.

    Returns:
        Dictionary with all relation counts initialized to zero
    """
    dic = {}
    for rel in ALLEN_RELATION_ORDER:
        dic[rel] = 0
    return dic


def updateTally(pBorn, pDie, dic):
    """
    Update the global tally with results from a simulation.

    Args:
        pBorn: Birth probability
        pDie: Death probability
        dic: Dictionary of relation frequencies
    """
    pStr = str(pBorn) + "," + str(pDie)  # Converts pair to string for dictionary

    if pStr not in tally:
        tally[pStr] = arInitDic()

    for rel in ALLEN_RELATION_ORDER:
        tally[pStr][rel] = tally[pStr][rel] + dic[rel]


def probDic(dic, trials):
    """
    Convert frequency counts to probabilities.

    Args:
        dic: Dictionary of relation frequencies
        trials: Number of trials

    Returns:
        Dictionary of relation probabilities
    """
    # Use shared normalize_counts function instead of manual calculation
    return normalize_counts(dic)


def print_distribution(dic):
    """
    Print the distribution of Allen relations in a readable format.

    Args:
        dic: Dictionary of relation frequencies
    """
    total = sum(dic.values())
    if total == 0:
        print("  No data to display (zero total)")
        return

    print("  Allen Relation Distribution:")
    print("  ---------------------------")
    print("  Relation            Count     Probability")
    print("  ---------------------------")

    # Print relations in Alspaugh's order
    for rel in ALLEN_RELATION_ORDER:
        count = dic[rel]
        prob = count / total if total > 0 else 0
        name = get_relation_name(rel)
        print(f"  {rel}: {name:<15} {count:5}     {prob:.6f}")

    print("  ---------------------------")
    print(f"  Total                {total:5}     1.000000")


def test_uniform_distribution(dic):
    """
    Test whether the observed relation distribution follows a uniform distribution.

    This tests the null hypothesis that all Allen relations are equally probable.

    Args:
        dic: Dictionary of relation frequencies
    """
    counts = [dic[rel] for rel in ALLEN_RELATION_ORDER]
    total = sum(counts)

    if total == 0:
        print("  Not enough data for hypothesis testing")
        return

    # Expected frequencies under uniform distribution
    expected = [total / len(ALLEN_RELATION_ORDER)] * len(ALLEN_RELATION_ORDER)

    # Chi-square test for uniform distribution
    chi2, p_value = stats.chisquare(counts, expected)

    print("\n  Uniform Distribution Hypothesis Test:")
    print("  ----------------------------------")
    print(f"  Chi-square statistic: {chi2:.4f}")
    print(f"  p-value: {p_value:.8f}")

    if p_value < 0.05:
        print(
            "  Conclusion: Reject null hypothesis (relations are NOT uniformly distributed)"
        )
    else:
        print(
            "  Conclusion: Fail to reject null hypothesis (relations may be uniformly distributed)"
        )


def generate_composition_table(pBorn, pDie, trials):
    """
    Generate a probabilistic composition table through simulation.

    For each pair of relations, simulate intervals and measure the resulting
    composition relation probabilities.

    Args:
        pBorn: Birth probability
        pDie: Death probability
        trials: Number of trials per relation pair
    """
    # Initialize composition tally
    for rel1 in ALLEN_RELATION_ORDER:
        for rel2 in ALLEN_RELATION_ORDER:
            key = f"{rel1},{rel2}"
            composition_tally[key] = arInitDic()

    # Run simulation for each relation pair
    print(f"Simulating with pBorn={pBorn}, pDie={pDie}, trials={trials}")

    # Generate histories
    histories = simulateRed(pBorn, pDie, trials)

    # For each history, identify relations between intervals and their composition
    for hist in histories:
        # Split history into interval pairs (0-1, 1-2, 0-2)
        # This is complex and would require custom logic to extract relations
        # For demonstration, we'll use the theoretical composition from relations.py
        pass

    # For demonstration, using theoretical compositions for a simplified example
    print("\nTheoretical Composition Table (Subset):")
    print("------------------------------------")
    print("rel1 ∘ rel2 = potential relations")

    # Show sample compositions from a few key relations
    sample_relations = ["p", "m", "o", "e", "d"]
    for rel1 in sample_relations:
        for rel2 in sample_relations:
            composition = compose_relations(rel1, rel2)
            print(f"{rel1} ∘ {rel2} = {composition}")

    print("\nTo generate the full probabilistic composition table,")
    print(
        "additional logic would be needed to extract relations from simulated histories."
    )


def talProb():
    """
    Calculate probabilities from tallies across all parameter settings.

    Returns:
        Dictionary mapping parameter settings to relation probabilities
    """
    temp = {}
    for k in tally:
        temp[k] = probDic(tally[k], sum(tally[k].values()))
    return temp


def tallyProb(pBorn, pDie):
    """
    Get probabilities for a specific parameter setting.

    Args:
        pBorn: Birth probability
        pDie: Death probability

    Returns:
        Dictionary of relation probabilities
    """
    key = f"{pBorn},{pDie}"
    if key in tally:
        return probDic(tally[key], sum(tally[key].values()))
    return None


def checkSum(dic):
    """
    Calculate the sum of all values in a dictionary.

    Args:
        dic: Dictionary of values

    Returns:
        Sum of all values
    """
    return sum(dic.values())


def ta2file(file):
    """
    Write tally data to a file.

    Args:
        file: Filename to write to
    """
    w2file(file, "Allen Interval Relation Tallies")
    w2file(file, "==========================")

    for p in tally:
        w2file(file, f"{checkSum(tally[p])} trials of {p}")
        w2file(file, str(tally[p]))
    w2file(file, "\n")


def pr2file(file):
    """
    Write probability data to a file.

    Args:
        file: Filename to write to
    """
    dic = talProb()
    w2file(file, "Allen Interval Relation Probabilities")
    w2file(file, "==================================")

    for p in dic:
        w2file(file, f"{p}:")
        w2file(file, str(dic[p]))
    w2file(file, "\n")


def w2file(file, content):
    """
    Append text to a file.

    Args:
        file: Filename to append to
        content: Content to write
    """
    try:
        with open(file, "a") as f:
            f.write(str(content) + "\n")
    except:
        print("Unable to append to file")


def visualize_relation_distribution(pBorn, pDie):
    """
    Visualize the distribution of Allen relations for a given parameter setting.

    Args:
        pBorn: Birth probability
        pDie: Death probability
    """
    key = f"{pBorn},{pDie}"
    if key not in tally:
        print(f"No data for pBorn={pBorn}, pDie={pDie}")
        return

    probs = tallyProb(pBorn, pDie)

    plt.figure(figsize=(12, 6))
    plt.bar(ALLEN_RELATION_ORDER, [probs[rel] for rel in ALLEN_RELATION_ORDER])
    plt.axhline(
        y=1 / 13, color="r", linestyle="--", label="Uniform distribution (1/13)"
    )
    plt.xlabel("Allen Relations")
    plt.ylabel("Probability")
    plt.title(f"Allen Relation Distribution (pBorn={pBorn}, pDie={pDie})")
    plt.ylim(0, max([probs[rel] for rel in ALLEN_RELATION_ORDER]) * 1.1)
    plt.legend()
    plt.savefig(f"allen_distribution_{pBorn}_{pDie}.png")
    plt.close()

    print(f"Visualization saved as allen_distribution_{pBorn}_{pDie}.png")


# If run as main script
if __name__ == "__main__":
    demo(use_seed=True, trials=10000)

    # Generate visualizations for a few key parameter settings
    for pBorn, pDie in [(0.1, 0.1), (0.01, 0.01), (0.2, 0.1)]:
        visualize_relation_distribution(pBorn, pDie)
