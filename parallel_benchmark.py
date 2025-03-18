"""
Benchmark script to compare sequential vs parallel simulation performance.

This script runs Allen interval simulations both sequentially and in parallel,
and reports the performance differences between the approaches.
"""

import time
import multiprocessing
from simulations import IntervalSimulator, set_random_seed
from analysis_utils import format_uniformity_test_results
from simulations import get_cache_stats, clear_cache


def run_benchmark(trials=100000, pBorn=0.1, pDie=0.1, use_cache=False):
    """
    Run a benchmark comparing sequential and parallel simulation performance.

    Args:
        trials: Number of simulation trials to run
        pBorn: Birth probability to use
        pDie: Death probability to use
        use_cache: Whether to use caching (for testing cache performance)
    """
    print(f"Benchmarking with {trials} trials (pBorn={pBorn}, pDie={pDie})")
    print(f"System has {multiprocessing.cpu_count()} CPU cores available")
    print(f"Cache enabled: {use_cache}")
    print("-" * 60)

    # Clear cache to ensure clean benchmark if not testing cache
    if not use_cache:
        clear_cache()

    # Set random seed for reproducibility
    set_random_seed(42)

    # Sequential simulation
    print("\nRunning sequential simulation...")
    seq_simulator = IntervalSimulator(pBorn, pDie, trials)
    seq_simulator.use_cache = use_cache
    seq_start = time.time()
    seq_results, seq_test = seq_simulator.simulate(
        test_uniformity=True, force_recompute=not use_cache
    )
    seq_time = time.time() - seq_start

    print(f"Sequential time: {seq_time:.2f} seconds")
    print(f"Sequential throughput: {trials / seq_time:.1f} trials/second")
    print(f"Test results: {format_uniformity_test_results(seq_test)}")

    # Parallel simulation with default settings (all cores)
    print("\nRunning parallel simulation (all cores)...")
    par_simulator = IntervalSimulator(pBorn, pDie, trials)
    par_simulator.use_cache = use_cache
    par_start = time.time()
    par_results, par_test = par_simulator.simulate_parallel(
        test_uniformity=True, force_recompute=not use_cache
    )
    par_time = time.time() - par_start

    print(f"Parallel time: {par_time:.2f} seconds")
    print(f"Parallel throughput: {trials / par_time:.1f} trials/second")
    print(f"Test results: {format_uniformity_test_results(par_test)}")

    # Print cache stats
    print("\nCache Statistics:")
    stats = get_cache_stats()
    for key, value in stats.items():
        if key == "hit_ratio":
            print(f"  {key}: {value:.2%}")
        else:
            print(f"  {key}: {value}")

    # Calculate speedup
    speedup = seq_time / par_time
    efficiency = speedup / multiprocessing.cpu_count() * 100

    print("\nPerformance comparison:")
    print(f"Speedup: {speedup:.2f}x faster with parallel execution")
    print(f"Parallel efficiency: {efficiency:.1f}%")

    # Verify results are consistent
    results_match = all(seq_results[rel] == par_results[rel] for rel in seq_results)
    print(
        f"Results consistency check: {'PASS' if results_match else 'FAIL - results differ'}"
    )

    # Test batch execution
    print("\nRunning batch execution (10 batches)...")
    batch_simulator = IntervalSimulator(pBorn, pDie, trials)
    batch_start = time.time()
    batch_results = batch_simulator.simulate_batches(n_batches=10, show_progress=True)
    batch_time = time.time() - batch_start

    print(f"Batch execution time: {batch_time:.2f} seconds")
    print(f"Batch throughput: {trials / batch_time:.1f} trials/second")


if __name__ == "__main__":
    # Run a moderate-sized benchmark by default
    run_benchmark(trials=100000)

    # Example of running a larger benchmark
    # run_benchmark(trials=1000000)
