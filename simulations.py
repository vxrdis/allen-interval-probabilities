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
    identify_relation,  # Import the identify_relation function
)
from shared_utils import normalize_counts
from analysis_utils import (
    test_uniform_distribution,
    print_uniformity_test_results,
    perform_uniformity_test,
    analyze_distribution,
    format_uniformity_test_results,
)


# Replace global dictionaries with a registry class
class SimulatorRegistry:
    """Registry that maintains a collection of all simulation results."""

    def __init__(self):
        self.simulators = {}  # Dictionary mapping param strings to simulators

    def register_simulator(self, simulator):
        """Register a simulator in the registry."""
        key = f"{simulator.pBorn},{simulator.pDie}"
        if key not in self.simulators:
            self.simulators[key] = simulator
        return simulator

    def get_simulator(self, pBorn, pDie):
        """Get a simulator by birth and death probabilities."""
        key = f"{pBorn},{pDie}"
        return self.simulators.get(key, None)

    def get_or_create_simulator(self, pBorn, pDie, trials=1000):
        """Get an existing simulator or create a new one if it doesn't exist."""
        simulator = self.get_simulator(pBorn, pDie)
        if not simulator:
            simulator = IntervalSimulator(pBorn, pDie, trials)
        return simulator

    def get_all_simulators(self):
        """Get all registered simulators."""
        return self.simulators.values()

    def get_tally(self, pBorn, pDie):
        """Get the tally for specific parameters."""
        simulator = self.get_simulator(pBorn, pDie)
        if simulator:
            return simulator.tally.get(simulator.param_key, {})
        return {}

    def get_all_tallies(self):
        """Get all tallies from all simulators."""
        all_tallies = {}
        for key, simulator in self.simulators.items():
            all_tallies[key] = simulator.tally.get(simulator.param_key, {})
        return all_tallies

    def get_all_probabilities(self):
        """Get all probability distributions from all simulators."""
        all_probs = {}
        for key, simulator in self.simulators.items():
            all_probs[key] = simulator.get_probabilities()
        return all_probs

    def reset_all(self):
        """Reset all simulators in the registry."""
        for simulator in self.simulators.values():
            simulator.reset()


# Create a global registry instance
registry = SimulatorRegistry()

# Create a helper simulator for utility functions that need simulator methods
# but don't need a specific parameter set
utility_simulator = None


def get_utility_simulator():
    """Get or create the utility simulator singleton."""
    global utility_simulator
    if utility_simulator is None:
        utility_simulator = IntervalSimulator(0.1, 0.1, 1)
    return utility_simulator


class IntervalSimulator:
    def __init__(self, pBorn, pDie, trials):
        """
        Initialize the interval simulator with given parameters.

        Args:
            pBorn: Probability of transition from unborn to alive
            pDie: Probability of transition from alive to dead
            trials: Number of simulation trials to run
        """
        self.pBorn = pBorn
        self.pDie = pDie
        self.trials = trials
        self.results = None

        # Store simulation state in instance variables
        self.tally = {}
        self.simulation_count = 0
        self.composition_tally = {}

        # Initialize tally with current parameters
        self.param_key = f"{pBorn},{pDie}"
        self.tally[self.param_key] = self._init_relation_dict()

        # Register this simulator with the registry
        registry.register_simulator(self)

    def reset(self):
        """
        Reset the simulator to its initial state, clearing all results and tallies.

        This is useful when you want to reuse the same simulator for a fresh set
        of simulations without the influence of previous runs.

        Returns:
            self (for method chaining)
        """
        self.results = None
        self.tally = {}
        self.simulation_count = 0
        self.composition_tally = {}

        # Re-initialize tally with current parameters
        self.tally[self.param_key] = self._init_relation_dict()

        return self

    def simulate(self, test_uniformity=False, print_results=False):
        """
        Run Allen relation simulation with the specified parameters.

        This method simulates interval state transitions and counts the
        occurrences of each Allen relation type.

        Args:
            test_uniformity: Whether to test the result distribution for uniformity
            print_results: Whether to print the uniformity test results

        Returns:
            If test_uniformity is False: Dictionary of relation frequencies
            If test_uniformity is True: Tuple of (freq_dict, test_results_dict)
        """
        redRuns = self._simulate_intervals()
        dic = self._score_runs(redRuns)
        self.results = dic

        # Update instance tally
        self._update_tally(dic)
        self.simulation_count += 1

        # Test for uniform distribution if requested
        if test_uniformity:
            test_results = test_uniform_distribution(dic)

            if print_results:
                print_uniformity_test_results(test_results)

            return dic, test_results

        return dic

    def generate_composition_table(self, additional_trials=None):
        """
        Generate a probabilistic composition table through simulation.

        Args:
            additional_trials: If specified, run this many additional trials
                               for composition analysis

        Returns:
            Dictionary mapping relation pairs to resulting relation distributions
        """
        trials_to_use = additional_trials if additional_trials else self.trials

        # Initialize composition tally if not already done
        if not self.composition_tally:
            for rel1 in ALLEN_RELATION_ORDER:
                for rel2 in ALLEN_RELATION_ORDER:
                    key = f"{rel1},{rel2}"
                    self.composition_tally[key] = self._init_relation_dict()

        # Generate histories - either use existing results or simulate new ones
        if additional_trials:
            histories = self._simulate_intervals()
        else:
            # We'd need to extract or re-simulate the histories
            histories = self._simulate_intervals()

        # For demonstration, using theoretical compositions for a simplified example
        # In a full implementation, you'd extract relations from the histories
        return self.composition_tally

    def get_results(self):
        """
        Get both the raw frequency counts and probability distribution.

        Returns:
            Tuple containing (frequencies_dict, probabilities_dict)
        """
        if self.results is None:
            self.simulate()

        # Return both raw frequencies and normalized probabilities
        return self.results, self.get_probabilities()

    def get_probabilities(self):
        """
        Convert frequency counts to probabilities.

        Returns:
            Dictionary of relation probabilities
        """
        if self.results is None:
            self.simulate()
        return normalize_counts(self.results)

    def get_tally(self):
        """
        Get the accumulated tally of relation frequencies across all simulations.

        Returns:
            Dictionary of tallies by parameter settings
        """
        return self.tally

    def get_tally_probabilities(self):
        """
        Get the probability distribution from the accumulated tally.

        Returns:
            Dictionary of relation probabilities based on accumulated tallies
        """
        return {k: normalize_counts(v) for k, v in self.tally.items()}

    def test_uniform_distribution(self):
        """
        Test whether the observed relation distribution follows a uniform distribution.

        Returns:
            Dictionary containing test results (see analysis_utils.test_uniform_distribution)
        """
        if self.results is None:
            self.simulate()

        return test_uniform_distribution(self.results)

    def get_distribution_analysis(self):
        """
        Get a comprehensive analysis of the simulation results distribution.

        Returns:
            Dictionary containing analysis results including counts, probabilities,
            uniformity test, entropy, and other statistics.
        """
        if self.results is None:
            self.simulate()

        return analyze_distribution(self.results)

    def print_distribution(self):
        """Print the distribution of Allen relations in a readable format."""
        if self.results is None:
            self.simulate()

        print(f"\nDistribution for pBorn={self.pBorn}, pDie={self.pDie}:")

        # Get the distribution analysis and print formatted results
        analysis = self.get_distribution_analysis()
        result_str = format_distribution_results(analysis)
        print(result_str)

        # Print uniformity test results
        print_uniformity_test_results(analysis["uniformity_test"])

        return analysis

    def _update_tally(self, results_dict):
        """
        Update the instance tally with results from a simulation.

        Args:
            results_dict: Dictionary of relation frequencies
        """
        if self.param_key not in self.tally:
            self.tally[self.param_key] = self._init_relation_dict()

        for rel in ALLEN_RELATION_ORDER:
            self.tally[self.param_key][rel] += results_dict[rel]

    def _simulate_intervals(self):
        """
        Simulate interval state transitions and produce histories.

        Returns:
            List of histories (state transitions)
        """
        temp = []
        for run in range(self.trials):
            hist = [[0, 0]]  # Both intervals start as unborn [a-state, b-state]

            # Continue until both intervals are dead
            while not (hist[-1] == [2, 2]):
                first = self._update_state(hist[-1][0])
                second = self._update_state(hist[-1][1])

                # Only append if state changed (avoid duplication)
                if not (hist[-1] == [first, second]):
                    hist.append([first, second])

            temp.append(hist)
        return temp

    def _update_state(self, state):
        """
        Update the state of an interval based on transition probabilities.

        Args:
            state: Current state (0=unborn, 1=alive, 2=dead)

        Returns:
            New state
        """
        toss = random.random()
        if state == 0 and toss < self.pBorn:
            return 1  # Transition from unborn to alive
        elif state == 1 and toss < self.pDie:
            return 2  # Transition from alive to dead
        else:
            return state  # No change

    def _score_runs(self, reducedRuns):
        """
        Score the reduced runs to count occurrences of each Allen relation.

        Args:
            reducedRuns: List of histories (state transitions)

        Returns:
            Dictionary counting occurrences of each relation
        """
        dic = self._init_relation_dict()
        for r in reducedRuns:
            relation_code = self._get_relation_code(r)
            if relation_code:  # Only count if valid relation is identified
                dic[relation_code] += 1
        return dic

    def _init_relation_dict(self):
        """
        Initialize dictionary with all Allen relations set to zero.

        Returns:
            Dictionary with all relation counts initialized to zero
        """
        dic = {}
        for rel in ALLEN_RELATION_ORDER:
            dic[rel] = 0
        return dic

    def _get_relation_code(self, Hist):
        """
        Identify the Allen relation corresponding to a history of state transitions.

        This function converts interval transition histories to endpoint sequences
        and uses identify_relation from relations.py.

        Args:
            Hist: History of state transitions

        Returns:
            Allen relation code or None if no match
        """
        # Convert history to endpoint sequence for identify_relation
        endpoint_sequence = self._history_to_endpoint_sequence(Hist)
        if endpoint_sequence:
            # Use intervals 'a' and 'b' for the two intervals in the simulation
            return identify_relation(endpoint_sequence, "a", "b")
        return None

    def _history_to_endpoint_sequence(self, Hist):
        """
        Convert a state transition history to an endpoint sequence for identify_relation.

        The mappings preserve the inverse relation pattern from Alspaugh's notation:
        - p (precedes) <-> P (preceded-by): Swapping intervals reverses the relation
        - m (meets) <-> M (met-by): Swapping intervals reverses the relation
        - o (overlaps) <-> O (overlapped-by): Swapping intervals reverses the relation
        - F (finished-by) <-> f (finishes): Swapping intervals reverses the relation
        - D (contains) <-> d (during): Swapping intervals reverses the relation
        - s (starts) <-> S (started-by): Swapping intervals reverses the relation
        - e (equals) <-> e (equals): Self-inverse (symmetric relation)

        Args:
            Hist: History of state transitions like [[0, 0], [1, 1], [2, 2]]

        Returns:
            List of sets representing endpoint configurations or None if mapping not defined
        """
        # Map histories to endpoint sequences using Alspaugh's notation
        # The mapping preserves the original arCode mapping logic but uses identify_relation format
        from relations import l, r  # Import endpoint identifier functions

        la, ra = l("a"), r("a")  # Endpoints for interval a
        lb, rb = l("b"), r("b")  # Endpoints for interval b

        # Direct mappings from histories to endpoint configurations
        if Hist == [[0, 0], [1, 1], [2, 2]]:
            return [{la, lb}, {ra, rb}]  # Equal (e): la=lb, ra=rb (self-inverse)
        elif Hist == [[0, 0], [1, 0], [2, 0], [2, 1], [2, 2]]:
            return [
                {la},
                {ra},
                {lb},
                {rb},
            ]  # Before/Precedes (p): la<ra<lb<rb (inverse of P)
        elif Hist == [[0, 0], [0, 1], [0, 2], [1, 2], [2, 2]]:
            return [{lb}, {rb}, {la}, {ra}]  # After (P): lb<rb<la<ra (inverse of p)
        elif Hist == [[0, 0], [1, 0], [1, 1], [2, 1], [2, 2]]:
            return [{la}, {lb}, {ra}, {rb}]  # Overlaps (o): la<lb<ra<rb (inverse of O)
        elif Hist == [[0, 0], [0, 1], [1, 1], [1, 2], [2, 2]]:
            return [
                {lb},
                {la},
                {rb},
                {ra},
            ]  # Overlapped-by (O): lb<la<rb<ra (inverse of o)
        elif Hist == [[0, 0], [1, 0], [2, 1], [2, 2]]:
            return [{la}, {ra, lb}, {rb}]  # Meets (m): la<(ra=lb)<rb (inverse of M)
        elif Hist == [[0, 0], [0, 1], [1, 2], [2, 2]]:
            return [{lb}, {rb, la}, {ra}]  # Met-by (M): lb<(rb=la)<ra (inverse of m)
        elif Hist == [[0, 0], [0, 1], [1, 1], [2, 1], [2, 2]]:
            return [{lb}, {la}, {ra}, {rb}]  # During (d): lb<la<ra<rb (inverse of D)
        elif Hist == [[0, 0], [1, 0], [1, 1], [1, 2], [2, 2]]:
            return [{la}, {lb}, {rb}, {ra}]  # Contains (D): la<lb<rb<ra (inverse of d)
        elif Hist == [[0, 0], [1, 1], [2, 1], [2, 2]]:
            return [{la, lb}, {ra}, {rb}]  # Starts (s): la=lb, ra<rb (inverse of S)
        elif Hist == [[0, 0], [1, 1], [1, 2], [2, 2]]:
            return [{la, lb}, {rb}, {ra}]  # Started-by (S): la=lb, rb<ra (inverse of s)
        elif Hist == [[0, 0], [0, 1], [1, 1], [2, 2]]:
            return [{lb}, {la}, {ra, rb}]  # Finishes (f): lb<la, ra=rb (inverse of F)
        elif Hist == [[0, 0], [1, 0], [1, 1], [2, 2]]:
            return [
                {la},
                {lb},
                {ra, rb},
            ]  # Finished-by (F): la<lb, ra=rb (inverse of f)

        return None  # No match

    def save_results_to_file(self, filename):
        """
        Save simulation results to a file.

        Args:
            filename: Name of the file to save to
        """
        try:
            with open(filename, "a") as f:
                f.write("Allen Interval Relation Simulation Results\n")
                f.write("======================================\n")

                # Write parameters and trial count
                f.write(f"Parameters: pBorn={self.pBorn}, pDie={self.pDie}\n")
                f.write(f"Total trials: {self.simulation_count * self.trials}\n\n")

                # Write raw counts
                f.write("Relation Frequencies:\n")
                if self.param_key in self.tally:
                    total = sum(self.tally[self.param_key].values())
                    f.write(f"Total counts: {total}\n")
                    for rel in ALLEN_RELATION_ORDER:
                        count = self.tally[self.param_key][rel]
                        name = get_relation_name(rel)
                        f.write(f"{rel} ({name}): {count}\n")

                    # Write probabilities
                    probs = normalize_counts(self.tally[self.param_key])
                    f.write("\nRelation Probabilities:\n")
                    for rel in ALLEN_RELATION_ORDER:
                        name = get_relation_name(rel)
                        f.write(f"{rel} ({name}): {probs[rel]:.6f}\n")

                f.write("\n")

            print(f"Results saved to {filename}")
        except Exception as e:
            print(f"Error saving to file: {e}")

    def visualize_distribution(self, save_path=None):
        """
        Visualize the distribution of Allen relations.

        Args:
            save_path: If specified, save the plot to this file path
        """
        probs = self.get_probabilities()

        plt.figure(figsize=(12, 6))
        plt.bar(ALLEN_RELATION_ORDER, [probs[rel] for rel in ALLEN_RELATION_ORDER])
        plt.axhline(
            y=1 / 13, color="r", linestyle="--", label="Uniform distribution (1/13)"
        )
        plt.xlabel("Allen Relations")
        plt.ylabel("Probability")
        plt.title(f"Allen Relation Distribution (pBorn={self.pBorn}, pDie={self.pDie})")
        plt.ylim(0, max([probs[rel] for rel in ALLEN_RELATION_ORDER]) * 1.1)
        plt.legend()

        # Save to file if specified, otherwise show
        if save_path:
            plt.savefig(save_path)
            plt.close()
            print(f"Visualization saved as {save_path}")
        else:
            plt.show()


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

    simulators = []
    for pBorn, pDie in configs:
        # Create and use simulator
        simulator = IntervalSimulator(pBorn, pDie, trials)
        result, test_results = simulator.simulate(
            test_uniformity=True, print_results=False
        )

        # Print distribution and test results
        analysis = simulator.get_distribution_analysis()
        print(format_distribution_results(analysis))
        print(format_uniformity_test_results(test_results))

        print(
            f"\n  Uniformity Test: chi²={test_results['chi2']:.4f}, p={test_results['p_value']:.6f}"
        )
        print(f"  {test_results['conclusion']}\n")
        simulators.append(simulator)

    # Generate and display composition table for a specific config
    print("\n" + "=" * 80)
    print("Probabilistic Composition Table (pBorn=0.1, pDie=0.1):")
    print("=" * 80)

    # Find the simulator with desired parameters
    comp_simulator = registry.get_simulator(0.1, 0.1)
    if comp_simulator:
        comp_simulator.generate_composition_table(1000)

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

    # Save results to files
    print("\nSaving simulation results to file output_simulations.txt")

    # Create a new file with all simulation results
    with open("output_simulations.txt", "w") as f:
        f.write("Allen Interval Relation Simulation Results\n")
        f.write("=======================================\n\n")

    # Save individual simulator results
    for simulator in simulators:
        simulator.save_results_to_file("output_simulations.txt")

    print("Demo completed - results saved in output_simulations.txt")


# Updated versions of functions to use the simulator registry
def arSimulate(probBorn, probDie, trials, test_uniformity=False, print_results=False):
    """
    Run Allen relation simulation with specified birth/death probabilities.

    This function now uses or creates a simulator from the registry.

    Args:
        probBorn: Probability of transition from unborn to alive
        probDie: Probability of transition from alive to dead
        trials: Number of trials to run
        test_uniformity: Whether to test the result distribution for uniformity
        print_results: Whether to print the uniformity test results

    Returns:
        If test_uniformity is False: Dictionary of relation frequencies
        If test_uniformity is True: Tuple of (freq_dict, test_results_dict)
    """
    # Get existing simulator or create a new one
    simulator = registry.get_or_create_simulator(probBorn, probDie, trials)
    return simulator.simulate(
        test_uniformity=test_uniformity, print_results=print_results
    )


def talProb():
    """
    Calculate probabilities from tallies across all parameter settings.

    Returns:
        Dictionary mapping parameter settings to relation probabilities
    """
    return registry.get_all_probabilities()


def tallyProb(pBorn, pDie):
    """
    Get probabilities for a specific parameter setting.

    Args:
        pBorn: Birth probability
        pDie: Death probability

    Returns:
        Dictionary of relation probabilities
    """
    simulator = registry.get_simulator(pBorn, pDie)
    if simulator:
        return simulator.get_probabilities()
    return None


def ta2file(file):
    """
    Write tally data to a file.

    Args:
        file: Filename to write to
    """
    w2file(file, "Allen Interval Relation Tallies")
    w2file(file, "==========================")

    all_tallies = registry.get_all_tallies()
    for p, counts in all_tallies.items():
        w2file(file, f"{sum(counts.values())} trials of {p}")
        w2file(file, str(counts))
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

    for p, probs in dic.items():
        w2file(file, f"{p}:")
        w2file(file, str(probs))
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
    simulator = registry.get_simulator(pBorn, pDie)
    if not simulator:
        print(f"No data for pBorn={pBorn}, pDie={pDie}")
        return

    save_path = f"allen_distribution_{pBorn}_{pDie}.png"
    simulator.visualize_distribution(save_path)


# Refactored legacy functions to use simulators from the registry
def simulateRed(pBorn, pDie, trials):
    """
    Legacy function using simulators from the registry.

    This now reuses existing simulators when possible.
    """
    simulator = registry.get_or_create_simulator(pBorn, pDie, trials)
    return simulator._simulate_intervals()


def scoreRed(reducedRuns):
    """Legacy helper function using utility simulator"""
    return get_utility_simulator()._score_runs(reducedRuns)


def updateState(state, pBorn, pDie):
    """
    Legacy helper function using simulators from the registry

    This tries to find an existing simulator with matching parameters.
    """
    simulator = registry.get_or_create_simulator(pBorn, pDie, 1)
    return simulator._update_state(state)


def arCode(Hist):
    """
    Legacy helper function using identify_relation from relations.py

    This preserves backward compatibility by translating histories to endpoint sequences.
    """
    # Create a temporary simulator to use its conversion method
    simulator = get_utility_simulator()
    endpoint_sequence = simulator._history_to_endpoint_sequence(Hist)
    if endpoint_sequence:
        return identify_relation(endpoint_sequence, "a", "b")
    return None


def arInitDic():
    """Legacy helper function using utility simulator"""
    return get_utility_simulator()._init_relation_dict()


def probDic(dic, trials):
    """Legacy helper - normalizes counts to probabilities"""
    return normalize_counts(dic)


def print_distribution(dic):
    """
    Get a formatted representation of the Allen relation distribution.

    Args:
        dic: Dictionary of relation frequencies

    Returns:
        Dictionary containing analysis results and formatted string representation
    """
    analysis = analyze_distribution(dic)

    # Print the formatted results
    total = analysis["total_observations"]
    if total == 0:
        print("  No data to display (zero total)")
        return analysis

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

    return analysis


def format_distribution_results(analysis):
    """
    Format distribution analysis results as a readable string.

    Args:
        analysis: Dictionary from analyze_distribution()

    Returns:
        Formatted string representation of distribution results
    """
    result = "  Allen Relation Distribution:\n"
    result += "  ---------------------------\n"
    result += "  Relation            Count     Probability\n"
    result += "  ---------------------------\n"

    total = analysis["total_observations"]

    # Format each relation's statistics
    for rel in ALLEN_RELATION_ORDER:
        count = analysis["counts"][rel]
        prob = analysis["probabilities"][rel]
        name = get_relation_name(rel)
        result += f"  {rel}: {name:<15} {count:5}     {prob:.6f}\n"

    result += "  ---------------------------\n"
    result += f"  Total                {total:5}     1.000000\n"

    # Add entropy information
    result += f"\n  Shannon entropy: {analysis['entropy']:.4f} bits\n"

    # Add most/least common information
    most_common = analysis["most_common"]
    least_common = analysis["least_common"]

    result += f"  Most common: {most_common['label']} ({get_relation_name(most_common['label'])}): {most_common['probability']:.4f}\n"
    result += f"  Least common: {least_common['label']} ({get_relation_name(least_common['label'])}): {least_common['probability']:.4f}\n"

    return result


def checkSum(dic):
    """
    Calculate the sum of all values in a dictionary.

    Args:
        dic: Dictionary of values

    Returns:
        Sum of all values
    """
    return sum(dic.values())


# If run as main script
if __name__ == "__main__":
    demo(use_seed=True, trials=10000)

    # Generate visualizations for a few key parameter settings
    for pBorn, pDie in [(0.1, 0.1), (0.01, 0.01), (0.2, 0.1)]:
        visualize_relation_distribution(pBorn, pDie)
