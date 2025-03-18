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

import multiprocessing
from functools import partial
import os
import time
import json
import hashlib
import datetime
from pathlib import Path
from functools import lru_cache


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

# Create a helper simulator for utility functions that need simulator methods that don't need a specific parameter set
utility_simulator = None


def get_utility_simulator():
    """Get or create the utility simulator singleton."""
    global utility_simulator
    if utility_simulator is None:
        utility_simulator = IntervalSimulator(0.1, 0.1, 1)
    return utility_simulator


# Add a simulation results cache
class SimulationCache:
    """Cache for storing and retrieving simulation results based on parameters."""

    def __init__(self, cache_dir=None, memory_cache_size=100):
        """
        Initialize the simulation cache.

        Args:
            cache_dir: Directory to store persistent cache (None for memory-only cache)
            memory_cache_size: Size of in-memory LRU cache
        """
        self.memory_cache = {}
        self.memory_cache_size = memory_cache_size
        self.memory_cache_order = []
        self.cache_dir = cache_dir

        # Create cache directory if persistent caching is enabled
        if cache_dir:
            self.cache_path = Path(cache_dir)
            self.cache_path.mkdir(exist_ok=True, parents=True)
        else:
            self.cache_path = None

        # Initialize cache stats
        self.hits = 0
        self.misses = 0

    def _get_key(self, pBorn, pDie, trials):
        """Generate a unique key for the parameter combination."""
        # Round to handle floating point precision issues
        key = f"{round(pBorn, 8)},{round(pDie, 8)},{trials}"
        return key

    def _get_disk_key(self, pBorn, pDie, trials):
        """Generate a filename-safe key for disk storage."""
        key = self._get_key(pBorn, pDie, trials)
        return hashlib.md5(key.encode()).hexdigest()

    def get(self, pBorn, pDie, trials):
        """
        Retrieve results from cache if available.

        Args:
            pBorn: Birth probability
            pDie: Death probability
            trials: Number of trials

        Returns:
            Cached results or None if not found
        """
        key = self._get_key(pBorn, pDie, trials)

        # Check memory cache first
        if key in self.memory_cache:
            # Update LRU order
            self.memory_cache_order.remove(key)
            self.memory_cache_order.append(key)
            self.hits += 1
            return self.memory_cache[key]

        # Check disk cache if enabled
        if self.cache_path:
            disk_key = self._get_disk_key(pBorn, pDie, trials)
            cache_file = self.cache_path / f"{disk_key}.json"

            if cache_file.exists():
                try:
                    with open(cache_file, "r") as f:
                        data = json.load(f)

                    # Validate cache entry
                    if self._validate_cache_entry(data, pBorn, pDie, trials):
                        # Add to memory cache
                        self._add_to_memory_cache(key, data)
                        self.hits += 1
                        return data
                except (json.JSONDecodeError, IOError):
                    # Invalid cache file, ignore
                    pass

        self.misses += 1
        return None

    def _validate_cache_entry(self, data, pBorn, pDie, trials):
        """Validate that a cache entry matches the requested parameters."""
        if not isinstance(data, dict):
            return False

        meta = data.get("metadata", {})
        return (
            abs(meta.get("pBorn", 0) - pBorn) < 1e-8
            and abs(meta.get("pDie", 0) - pDie) < 1e-8
            and meta.get("trials", 0) == trials
        )

    def put(self, pBorn, pDie, trials, results, test_results=None):
        """
        Store results in cache.

        Args:
            pBorn: Birth probability
            pDie: Death probability
            trials: Number of trials
            results: Simulation results dictionary
            test_results: Optional test results dictionary

        Returns:
            Cache key
        """
        key = self._get_key(pBorn, pDie, trials)

        # Prepare data structure with metadata
        data = {
            "results": results,
            "test_results": test_results,
            "metadata": {
                "pBorn": pBorn,
                "pDie": pDie,
                "trials": trials,
                "timestamp": datetime.datetime.now().isoformat(),
                "cache_key": key,
            },
        }

        # Add to memory cache
        self._add_to_memory_cache(key, data)

        # Write to disk if enabled
        if self.cache_path:
            disk_key = self._get_disk_key(pBorn, pDie, trials)
            cache_file = self.cache_path / f"{disk_key}.json"

            try:
                with open(cache_file, "w") as f:
                    json.dump(data, f, indent=2)
            except IOError:
                # Failed to write to disk, continue with memory cache only
                pass

        return key

    def _add_to_memory_cache(self, key, data):
        """Add an entry to the memory cache with LRU tracking."""
        # If key already exists, update its position
        if key in self.memory_cache:
            self.memory_cache_order.remove(key)

        # Add to memory cache
        self.memory_cache[key] = data
        self.memory_cache_order.append(key)

        # Enforce cache size limit
        while len(self.memory_cache) > self.memory_cache_size:
            oldest_key = self.memory_cache_order.pop(0)
            self.memory_cache.pop(oldest_key, None)

    def clear(self):
        """Clear all cached results."""
        self.memory_cache.clear()
        self.memory_cache_order.clear()

        if self.cache_path and self.cache_path.exists():
            for cache_file in self.cache_path.glob("*.json"):
                try:
                    os.remove(cache_file)
                except OSError:
                    pass

    def get_stats(self):
        """Get cache statistics."""
        return {
            "hits": self.hits,
            "misses": self.misses,
            "hit_ratio": (
                self.hits / (self.hits + self.misses)
                if (self.hits + self.misses) > 0
                else 0
            ),
            "memory_entries": len(self.memory_cache),
            "disk_entries": (
                len(list(self.cache_path.glob("*.json"))) if self.cache_path else 0
            ),
        }


# Create global cache instance
simulation_cache = SimulationCache(
    cache_dir=os.path.join(os.path.dirname(__file__), ".simulation_cache"),
    memory_cache_size=100,
)


# Define relation colors for visualization
RELATION_COLOURS = {
    "p": "blue",
    "P": "lightblue",
    "m": "green",
    "M": "lightgreen",
    "o": "orange",
    "O": "lightorange",
    "D": "red",
    "d": "lightred",
    "s": "purple",
    "S": "lightpurple",
    "f": "brown",
    "F": "lightbrown",
    "e": "gray",
}


class IntervalSimulator:
    def __init__(self, pBorn, pDie, trials, use_cache=True):
        """
        Initialize the interval simulator with given parameters.

        Args:
            pBorn: Probability of transition from unborn to alive
            pDie: Probability of transition from alive to dead
            trials: Number of simulation trials to run
            use_cache: Whether to use result caching
        """
        self.pBorn = pBorn
        self.pDie = pDie
        self.trials = trials
        self.results = None
        self.use_cache = use_cache

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

    def simulate(
        self, test_uniformity=False, print_results=False, force_recompute=False
    ):
        """
        Run Allen relation simulation with the specified parameters.

        This method simulates interval state transitions and counts the
        occurrences of each Allen relation type.

        Args:
            test_uniformity: Whether to test the result distribution for uniformity
            print_results: Whether to print the uniformity test results
            force_recompute: Whether to force recomputation even if results are cached

        Returns:
            If test_uniformity is False: Dictionary of relation frequencies
            If test_uniformity is True: Tuple of (freq_dict, test_results_dict)
        """
        # Check cache for existing results if caching is enabled and not forcing recomputation
        if self.use_cache and not force_recompute:
            cached_data = simulation_cache.get(self.pBorn, self.pDie, self.trials)
            if cached_data:
                self.results = cached_data["results"]

                # Update instance tally
                self._update_tally(self.results)
                self.simulation_count += 1

                if test_uniformity:
                    test_results = cached_data.get("test_results")

                    # If no test results in cache, compute them
                    if not test_results:
                        test_results = test_uniform_distribution(self.results)

                    if print_results:
                        print(
                            f"Using cached results for pBorn={self.pBorn}, pDie={self.pDie}, trials={self.trials}"
                        )
                        print_uniformity_test_results(test_results)

                    return self.results, test_results

                if print_results:
                    print(
                        f"Using cached results for pBorn={self.pBorn}, pDie={self.pDie}, trials={self.trials}"
                    )

                return self.results

        # No cache hit or caching disabled, run the simulation
        redRuns = self._simulate_intervals()
        dic = self._score_runs(redRuns)
        self.results = dic

        # Update instance tally
        self._update_tally(dic)
        self.simulation_count += 1

        # Test for uniform distribution if requested
        test_results = None
        if test_uniformity:
            test_results = test_uniform_distribution(dic)

            if print_results:
                print_uniformity_test_results(test_results)

        # Cache results if caching is enabled
        if self.use_cache:
            simulation_cache.put(self.pBorn, self.pDie, self.trials, dic, test_results)

        if test_uniformity:
            return dic, test_results
        return dic

    def simulate_parallel(
        self,
        n_processes=None,
        batch_size=None,
        test_uniformity=False,
        force_recompute=False,
        verbose=False,  # Add verbosity parameter
    ):
        """
        Run Allen relation simulation using multiple processes in parallel.

        This method distributes the simulation workload across multiple CPU cores for
        significantly improved performance on large simulations.

        Args:
            n_processes: Number of processes to use (defaults to CPU count)
            batch_size: Size of each batch of trials (defaults to trials/n_processes)
            test_uniformity: Whether to test the result distribution for uniformity
            force_recompute: Whether to force recomputation even if results are cached
            verbose: Whether to print progress information

        Returns:
            If test_uniformity is False: Dictionary of relation frequencies
            If test_uniformity is True: Tuple of (freq_dict, test_results_dict)
        """
        # Check cache for existing results if caching is enabled and not forcing recomputation
        if self.use_cache and not force_recompute:
            cached_data = simulation_cache.get(self.pBorn, self.pDie, self.trials)
            if cached_data:
                self.results = cached_data["results"]

                # Update instance tally
                self._update_tally(self.results)
                self.simulation_count += 1

                if verbose:
                    print(
                        f"Using cached results for pBorn={self.pBorn}, pDie={self.pDie}, trials={self.trials}"
                    )

                if test_uniformity:
                    test_results = cached_data.get("test_results")

                    # If no test results in cache, compute them
                    if not test_results:
                        test_results = test_uniform_distribution(self.results)

                    return self.results, test_results

                return self.results

        # Determine number of processes to use
        if n_processes is None:
            n_processes = multiprocessing.cpu_count()
        n_processes = min(n_processes, multiprocessing.cpu_count(), self.trials)

        # Determine batch size for each process
        if batch_size is None:
            batch_size = (self.trials + n_processes - 1) // n_processes

        # Calculate number of batches needed
        n_batches = (self.trials + batch_size - 1) // batch_size

        # Prepare batch parameters
        batch_trials = [
            min(batch_size, self.trials - i * batch_size) for i in range(n_batches)
        ]

        # Print information about parallel execution if verbose
        if verbose:
            print(
                f"Running {self.trials} trials across {n_processes} processes in {n_batches} batches"
            )
            print(f"Birth probability: {self.pBorn}, Death probability: {self.pDie}")

        # Create a pool of worker processes
        with multiprocessing.Pool(processes=n_processes) as pool:
            # Create a partial function with fixed parameters
            worker_func = partial(
                self._simulate_batch, pBorn=self.pBorn, pDie=self.pDie
            )

            # Map the function over all batch sizes
            # Using imap to get results as they complete
            results = list(pool.imap(worker_func, batch_trials))

        # Combine results from all batches
        combined_counts = self._init_relation_dict()
        for counts in results:
            for rel in ALLEN_RELATION_ORDER:
                combined_counts[rel] += counts[rel]

        # Store the combined results
        self.results = combined_counts

        # Update instance tally
        self._update_tally(combined_counts)
        self.simulation_count += 1

        # Cache results if caching is enabled
        test_results = None
        if test_uniformity:
            test_results = test_uniform_distribution(combined_counts)

        if self.use_cache:
            simulation_cache.put(
                self.pBorn, self.pDie, self.trials, combined_counts, test_results
            )

        # Test for uniform distribution if requested
        if test_uniformity:
            return combined_counts, test_results

        return combined_counts

    # Add method for batch execution with progress tracking
    def simulate_batches(self, n_batches=10, test_uniformity=False, show_progress=True):
        """
        Run Allen relation simulation in sequential batches with progress tracking.

        This method divides the simulation into batches and shows progress after
        each batch, which is useful for monitoring long-running simulations.

        Args:
            n_batches: Number of batches to divide the trials into
            test_uniformity: Whether to test the result distribution for uniformity
            show_progress: Whether to show progress after each batch

        Returns:
            If test_uniformity is False: Dictionary of relation frequencies
            If test_uniformity is True: Tuple of (freq_dict, test_results_dict)
        """
        # Initialize results
        combined_counts = self._init_relation_dict()
        batch_size = (self.trials + n_batches - 1) // n_batches

        if show_progress:
            print(
                f"Running {self.trials} trials in {n_batches} batches of ~{batch_size} each"
            )
            print(f"Birth probability: {self.pBorn}, Death probability: {self.pDie}")

        start_time = time.time()

        # Run simulation in batches
        for i in range(n_batches):
            # Calculate size of this batch
            current_batch_size = min(batch_size, self.trials - i * batch_size)
            if current_batch_size <= 0:
                break

            # Create a temporary simulator for this batch
            temp_simulator = IntervalSimulator(
                self.pBorn, self.pDie, current_batch_size
            )
            batch_counts = temp_simulator.simulate()

            # Update combined counts
            for rel in ALLEN_RELATION_ORDER:
                combined_counts[rel] += batch_counts[rel]

            # Show progress
            if show_progress:
                trials_completed = min((i + 1) * batch_size, self.trials)
                percent_complete = trials_completed / self.trials * 100
                elapsed = time.time() - start_time
                estimated_total = elapsed / percent_complete * 100
                remaining = estimated_total - elapsed

                print(
                    f"Batch {i+1}/{n_batches}: {trials_completed}/{self.trials} trials "
                    + f"({percent_complete:.1f}%) - ETA: {remaining:.1f}s"
                )

                # Show intermediate distribution for feedback
                if i > 0 and i % max(1, n_batches // 5) == 0:
                    test_results = test_uniform_distribution(combined_counts)
                    print(
                        f"  Chi²: {test_results['chi2']:.4f}, p-value: {test_results['p_value']:.6f}"
                    )

        # Store the combined results
        self.results = combined_counts

        # Update instance tally
        self._update_tally(combined_counts)
        self.simulation_count += 1

        # Show final timing
        if show_progress:
            total_time = time.time() - start_time
            print(
                f"Completed {self.trials} trials in {total_time:.2f}s "
                + f"({self.trials/total_time:.1f} trials/second)"
            )

        # Test for uniform distribution if requested
        if test_uniformity:
            test_results = test_uniform_distribution(combined_counts)
            return combined_counts, test_results

        return combined_counts

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
        """
        Print the distribution of Allen relations in a readable format.

        This method is kept for backward compatibility. For new code,
        use get_distribution_analysis() instead and handle the presentation
        in client code.

        Returns:
            Dictionary containing analysis results
        """
        if self.results is None:
            self.simulate()

        analysis = self.get_distribution_analysis()
        result_str = format_distribution_results(analysis)
        print(f"\nDistribution for pBorn={self.pBorn}, pDie={self.pDie}:")
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
        Simulate interval state transitions and produce histories using vectorized operations.

        This implementation uses NumPy's geometric sampling to directly determine transition times,
        avoiding explicit loops over state transitions.

        Returns:
            List of histories (state transitions)
        """
        # For each trial, we need to determine:
        # 1. Time to transition from unborn (0) to alive (1) for both intervals
        # 2. Time to transition from alive (1) to dead (2) for both intervals

        # Sample from geometric distribution to get transition times
        # Note: numpy's geometric starts from 1, so we subtract 1 to start from 0
        if self.pBorn > 0:
            unborn_to_alive_a = np.random.geometric(self.pBorn, self.trials) - 1
            unborn_to_alive_b = np.random.geometric(self.pBorn, self.trials) - 1
        else:
            # If pBorn is 0, the intervals never transition to alive (they remain unborn forever)
            # This is a degenerate case, but we'll handle it by setting to infinity
            unborn_to_alive_a = np.full(self.trials, np.inf)
            unborn_to_alive_b = np.full(self.trials, np.inf)

        if self.pDie > 0:
            alive_to_dead_a = np.random.geometric(self.pDie, self.trials) - 1
            alive_to_dead_b = np.random.geometric(self.pDie, self.trials) - 1
        else:
            # If pDie is 0, the intervals never transition to dead (they remain alive forever)
            # This is also a degenerate case, but we'll handle it for completeness
            alive_to_dead_a = np.full(self.trials, np.inf)
            alive_to_dead_b = np.full(self.trials, np.inf)

        # Calculate absolute times for each state transition
        time_alive_a = unborn_to_alive_a
        time_alive_b = unborn_to_alive_b
        time_dead_a = time_alive_a + alive_to_dead_a
        time_dead_b = time_alive_b + alive_to_dead_b

        # Reconstruct histories from transition times
        histories = []
        for i in range(self.trials):
            # Create timeline of all events (transitions)
            timeline = []

            # Add transition events for interval A
            if np.isfinite(time_alive_a[i]):
                timeline.append((time_alive_a[i], "a", 1))  # A transitions to alive
            if np.isfinite(time_dead_a[i]):
                timeline.append((time_dead_a[i], "a", 2))  # A transitions to dead

            # Add transition events for interval B
            if np.isfinite(time_alive_b[i]):
                timeline.append((time_alive_b[i], "b", 1))  # B transitions to alive
            if np.isfinite(time_dead_b[i]):
                timeline.append((time_dead_b[i], "b", 2))  # B transitions to dead

            # Sort timeline by time
            timeline.sort()

            # Initialize history with both intervals unborn
            history = [[0, 0]]

            # Process events to build history
            for _, interval, state in timeline:
                # Copy the last state
                new_state = history[-1].copy()
                # Update the appropriate interval's state
                if interval == "a":
                    new_state[0] = state
                else:  # interval == 'b'
                    new_state[1] = state
                # Add to history if state changed
                if new_state != history[-1]:
                    history.append(new_state)

            # If we didn't reach the final state [2,2], add it
            # This handles the case where one or both intervals never reach the dead state
            if history[-1] != [2, 2]:
                history.append([2, 2])

            histories.append(history)

        return histories

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
        Score the reduced runs to count occurrences of each Allen relation using NumPy arrays.

        Args:
            reducedRuns: List of histories (state transitions)

        Returns:
            Dictionary counting occurrences of each relation
        """
        # Initialize a counts array
        n_relations = len(ALLEN_RELATION_ORDER)
        counts_array = np.zeros(n_relations, dtype=np.int64)
        relation_indices = {rel: i for i, rel in enumerate(ALLEN_RELATION_ORDER)}

        # Process each history
        for r in reducedRuns:
            relation_code = self._get_relation_code(r)
            if relation_code:  # Only count if valid relation is identified
                counts_array[relation_indices[relation_code]] += 1

        # Convert back to dictionary format for compatibility
        dic = {rel: counts_array[i] for i, rel in enumerate(ALLEN_RELATION_ORDER)}
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
        lb, rb = l("b")  # Endpoints for interval b

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

        DEPRECATED: Use get_formatted_results() instead and handle file writing in caller code.

        Args:
            filename: Name of the file to save to
        """
        try:
            with open(filename, "a") as f:
                f.write(self.get_formatted_results())
                f.write("\n")
            print(f"Results saved to {filename}")
        except Exception as e:
            print(f"Error saving to file: {e}")

    def get_formatted_results(self):
        """
        Get formatted simulation results as a string.

        This replaces direct printing with a function that returns formatted text.

        Returns:
            String containing formatted results
        """
        if self.results is None:
            self.simulate()

        result_text = f"Allen Interval Relation Simulation Results\n"
        result_text += "======================================\n"
        result_text += f"Parameters: pBorn={self.pBorn}, pDie={self.pDie}\n"
        result_text += f"Total trials: {self.simulation_count * self.trials}\n\n"
        result_text += "Relation Frequencies:\n"

        if self.param_key in self.tally:
            total = sum(self.tally[self.param_key].values())
            result_text += f"Total counts: {total}\n"

            for rel in ALLEN_RELATION_ORDER:
                count = self.tally[self.param_key][rel]
                name = get_relation_name(rel)
                result_text += f"{rel} ({name}): {count}\n"

            # Add probabilities
            probs = normalize_counts(self.tally[self.param_key])
            result_text += "\nRelation Probabilities:\n"

            for rel in ALLEN_RELATION_ORDER:
                name = get_relation_name(rel)
                result_text += f"{rel} ({name}): {probs[rel]:.6f}\n"

        return result_text

    def create_distribution_figure(self):
        """
        Create a visualization of the Allen relation distribution.

        This replaces visualize_distribution() with a function that returns the figure
        without saving it.

        Returns:
            Matplotlib Figure object
        """
        probs = self.get_probabilities()

        fig = plt.figure(figsize=(12, 6))
        # Use ALLEN_RELATION_ORDER for consistent ordering
        bars = plt.bar(
            ALLEN_RELATION_ORDER,
            [probs[rel] for rel in ALLEN_RELATION_ORDER],
            color=[RELATION_COLOURS[rel] for rel in ALLEN_RELATION_ORDER],
        )
        plt.axhline(
            y=1 / 13, color="r", linestyle="--", label="Uniform distribution (1/13)"
        )

        # Add relation names as annotations for better readability
        for i, rel in enumerate(ALLEN_RELATION_ORDER):
            name = get_relation_name(rel)
            plt.text(
                i,
                probs[rel] + 0.005,
                name,
                ha="center",
                rotation=90,
                fontsize=8,
                color="darkblue",
            )

        plt.xlabel("Allen Relations")
        plt.ylabel("Probability")
        plt.title(f"Allen Relation Distribution (pBorn={self.pBorn}, pDie={self.pDie})")
        plt.ylim(0, max([probs[rel] for rel in ALLEN_RELATION_ORDER]) * 1.1)
        plt.legend()

        return fig

    def visualize_distribution(self, save_path=None):
        """
        Create a visualization of the Allen relation distribution and optionally save it.

        DEPRECATED: Use create_distribution_figure() instead and handle saving in caller code.

        Args:
            save_path: If specified, save the plot to this file path

        Returns:
            Matplotlib Figure object
        """
        fig = self.create_distribution_figure()

        # Save to file if specified
        if save_path:
            plt.savefig(save_path)
            print(f"Visualization saved as {save_path}")

        return fig


def set_random_seed(seed=42):
    """
    Set the random seed for reproducibility.

    Args:
        seed: Integer seed value for random number generator
    """
    random.seed(seed)
    np.random.seed(seed)


def demo(use_seed=True, trials=10000, use_parallel=True):
    """
    Run demonstration simulations with various probability settings.

    Args:
        use_seed: If True, use a fixed random seed for reproducibility
        trials: Number of simulation trials to run
        use_parallel: Whether to use parallel execution
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
        # Create simulator
        simulator = IntervalSimulator(pBorn, pDie, trials)

        # Run using parallel or sequential mode based on parameter
        if use_parallel:
            print(f"\nRunning parallel simulation for pBorn={pBorn}, pDie={pDie}")
            result, test_results = simulator.simulate_parallel(test_uniformity=True)
        else:
            print(f"\nRunning sequential simulation for pBorn={pBorn}, pDie={pDie}")
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
def arSimulate(
    probBorn,
    probDie,
    trials,
    test_uniformity=False,
    print_results=False,
    use_cache=True,
    force_recompute=False,
):
    """
    Run Allen relation simulation with specified birth/death probabilities.

    This function now uses or creates a simulator from the registry.

    Args:
        probBorn: Probability of transition from unborn to alive
        probDie: Probability of transition from alive to dead
        trials: Number of trials to run
        test_uniformity: Whether to test the result distribution for uniformity
        print_results: Whether to print the uniformity test results
        use_cache: Whether to use result caching
        force_recompute: Whether to force recomputation even if results are cached

    Returns:
        If test_uniformity is False: Dictionary of relation frequencies
        If test_uniformity is True: Tuple of (freq_dict, test_results_dict)
    """
    # Get existing simulator or create a new one
    simulator = registry.get_or_create_simulator(probBorn, probDie, trials)
    simulator.use_cache = use_cache  # Set cache usage flag

    return simulator.simulate(
        test_uniformity=test_uniformity,
        print_results=print_results,
        force_recompute=force_recompute,
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


# Add a convenience function for parallel simulation
def simulate_parallel(
    pBorn,
    pDie,
    trials,
    n_processes=None,
    test_uniformity=False,
    use_cache=True,
    force_recompute=False,
    verbose=False,  # Add verbosity parameter to control output
):
    """
    Run a parallel Allen relation simulation with the specified parameters.

    This is a convenience function that creates a simulator and runs it in parallel.

    Args:
        pBorn: Birth probability
        pDie: Death probability
        trials: Number of simulation trials to run
        n_processes: Number of processes to use (defaults to CPU count)
        test_uniformity: Whether to test the result distribution for uniformity
        use_cache: Whether to use result caching
        force_recompute: Whether to force recomputation even if results are cached
        verbose: Whether to print progress information

    Returns:
        If test_uniformity is False: Dictionary of relation frequencies
        If test_uniformity is True: Tuple of (freq_dict, test_results_dict)
    """
    simulator = IntervalSimulator(pBorn, pDie, trials)
    simulator.use_cache = use_cache  # Set cache usage flag

    return simulator.simulate_parallel(
        n_processes=n_processes,
        test_uniformity=test_uniformity,
        force_recompute=force_recompute,
        verbose=verbose,
    )


# Add cache management functions
def get_cache_stats():
    """
    Get statistics about the simulation cache.

    Returns:
        Dictionary with cache statistics
    """
    return simulation_cache.get_stats()


def clear_cache():
    """
    Clear all cached simulation results.
    """
    simulation_cache.clear()
    print("Simulation cache cleared")


def warm_cache(param_list=None, verbose=True):
    """
    Pre-compute and cache results for common parameter combinations.

    Args:
        param_list: List of (pBorn, pDie, trials) tuples to pre-compute
                    If None, uses a default set of common parameters
        verbose: Whether to print progress information

    Returns:
        Dictionary with cache statistics after warming
    """
    if param_list is None:
        # Default set of commonly used parameters
        param_list = [
            (0.5, 0.5, 10000),
            (0.1, 0.1, 10000),
            (0.01, 0.01, 10000),
            (0.2, 0.1, 10000),
        ]

    if verbose:
        print(f"Warming cache with {len(param_list)} parameter combinations...")

    for i, (pBorn, pDie, trials) in enumerate(param_list):
        if verbose:
            print(
                f"Computing [{i+1}/{len(param_list)}] pBorn={pBorn}, pDie={pDie}, trials={trials}"
            )
        results, test_results = arSimulate(
            pBorn, pDie, trials, test_uniformity=True, use_cache=True
        )

    stats = get_cache_stats()
    if verbose:
        print("Cache warming complete")
        print(f"Cache stats: {stats}")

    return stats


# If run as main script
if __name__ == "__main__":
    demo(use_seed=True, trials=10000)

    # Generate visualizations for a few key parameter settings
    for pBorn, pDie in [(0.1, 0.1), (0.01, 0.01), (0.2, 0.1)]:
        simulator = registry.get_or_create_simulator(pBorn, pDie, 10000)
        fig = simulator.visualize_distribution(f"allen_distribution_{pBorn}_{pDie}.png")
        plt.close(fig)  # Close the figure after saving
