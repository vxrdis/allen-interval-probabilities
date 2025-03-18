"""
Statistical Analysis Utilities for Allen's Interval Algebra

This module provides statistical analysis functions for working with Allen's interval
algebra distributions, including:

1. Uniformity testing via chi-square
2. Entropy calculation
3. Distribution comparison utilities

These functions help evaluate the statistical properties of relation distributions
and compare them with theoretical expectations.
"""

import numpy as np
import scipy.stats as stats
from constants import ALLEN_RELATION_ORDER
from shared_utils import normalize_counts


def test_uniform_distribution(observed_counts, labels=None):
    """
    Test whether an observed distribution follows a uniform distribution.

    This function handles two calling patterns:
    1. test_uniform_distribution(counts_dict) - where counts_dict is a dictionary mapping labels to counts
    2. test_uniform_distribution(observed_counts, labels) - where observed_counts is an array and labels is an array

    Args:
        observed_counts: Dictionary of relation frequencies OR array of observed counts
        labels: Optional array of category labels (used when observed_counts is an array)

    Returns:
        Dictionary containing test results:
        {
            'chi2': chi-square statistic,
            'p_value': p-value from the test,
            'reject_null': boolean indicating whether to reject the null hypothesis,
            'observed': original observed counts,
            'expected': expected counts under uniform distribution,
            'total_observations': total number of observations,
            'df': degrees of freedom,
            'alpha': significance level used (0.05)
        }
        Returns None if there's not enough data for the test.
    """
    # Handle the case where observed_counts is a dictionary
    if isinstance(observed_counts, dict):
        counts_dict = observed_counts
        # If labels are provided but we have a dict, ignore them with a warning
        if labels is not None:
            print(
                "Warning: labels parameter ignored when observed_counts is a dictionary"
            )

        # Convert dictionary to a list of counts in the standard order
        if all(rel in counts_dict for rel in ALLEN_RELATION_ORDER):
            # Use Allen relation order if all relations are present
            counts = [counts_dict[rel] for rel in ALLEN_RELATION_ORDER]
            labels = ALLEN_RELATION_ORDER
        else:
            # Otherwise use the dictionary keys as labels
            counts = list(counts_dict.values())
            labels = list(counts_dict.keys())

    # Handle the case where observed_counts is a list/array
    else:
        counts = observed_counts
        # If observed_counts is a list/array but no labels provided, we still proceed
        # since labels are only needed for identification, not for the statistical test
        if labels is None:
            labels = [f"Category_{i}" for i in range(len(counts))]

    # Convert to numpy array if not already
    counts = np.array(counts)
    total = np.sum(counts)

    if total == 0:
        return None

    # Expected frequencies under uniform distribution
    expected = np.full(len(counts), total / len(counts))

    # Chi-square test for uniform distribution
    chi2, p_value = stats.chisquare(counts, expected)

    # Degrees of freedom
    df = len(counts) - 1

    # Significance level
    alpha = 0.05

    # Create result dictionary
    result = {
        "chi2": float(chi2),  # Convert from numpy type to native Python type
        "p_value": float(p_value),
        "reject_null": p_value < alpha,
        "observed": counts.tolist(),  # Convert array to list for serialization
        "expected": expected.tolist(),
        "total_observations": int(total),
        "df": df,
        "alpha": alpha,
        "labels": labels,
        "conclusion": (
            "Reject uniform distribution"
            if p_value < alpha
            else "Cannot reject uniform distribution"
        ),
    }

    return result


def format_uniformity_test_results(test_results):
    """
    Format the uniformity test results as a string.

    Args:
        test_results: Dictionary from test_uniform_distribution()

    Returns:
        String with formatted test results
    """
    if test_results is None:
        return "Not enough data for hypothesis testing"

    formatted = "\n  Uniform Distribution Hypothesis Test:\n"
    formatted += "  ----------------------------------\n"
    formatted += f"  Chi-square statistic: {test_results['chi2']:.4f}\n"
    formatted += f"  p-value: {test_results['p_value']:.8f}\n"

    if test_results["reject_null"]:
        formatted += "  Conclusion: Reject null hypothesis (relations are NOT uniformly distributed)"
    else:
        formatted += "  Conclusion: Fail to reject null hypothesis (relations may be uniformly distributed)"

    return formatted


def print_uniformity_test_results(test_results):
    """
    Print the results of a uniformity test.

    DEPRECATED: Use format_uniformity_test_results() instead and handle printing in caller code.

    Args:
        test_results: Either a results dictionary from test_uniform_distribution()
                     or a tuple of (chi2, p_value) for backwards compatibility
    """
    # Handle backwards compatibility with old (chi2, p_value) tuple format
    if isinstance(test_results, tuple) and len(test_results) == 2:
        chi2, p_value = test_results
        if chi2 is None or p_value is None:
            print("  Not enough data for hypothesis testing")
            return

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
    else:
        # Handle new dictionary result format
        print(format_uniformity_test_results(test_results))


def perform_uniformity_test(counts_dict, verbose=False):
    """
    Perform a uniformity test and optionally print the results.

    Args:
        counts_dict: Dictionary of relation frequencies
        verbose: Whether to print the test results

    Returns:
        Dictionary containing test results (see test_uniform_distribution)
    """
    test_results = test_uniform_distribution(counts_dict)

    if verbose and test_results:
        print_uniformity_test_results(test_results)

    return test_results


def calculate_expected_frequencies(total_count, n_categories=None):
    """
    Calculate expected frequencies for a uniform distribution.

    Args:
        total_count: Total number of observations
        n_categories: Number of categories (defaults to 13 Allen relations)

    Returns:
        List of expected frequencies
    """
    if n_categories is None:
        n_categories = len(ALLEN_RELATION_ORDER)

    return [total_count / n_categories] * n_categories


def analyze_distribution(counts_dict):
    """
    Perform a complete analysis of a distribution, including uniformity test,
    entropy calculation, and descriptive statistics.

    Args:
        counts_dict: Dictionary of relation frequencies

    Returns:
        Dictionary containing analysis results
    """
    from shared_utils import calculate_shannon_entropy

    # Calculate probabilities
    probs = normalize_counts(counts_dict)

    # Get total observations
    total = sum(counts_dict.values())

    # Identify most and least common categories
    most_common = (
        max(counts_dict.items(), key=lambda x: x[1]) if counts_dict else (None, 0)
    )
    least_common = (
        min(counts_dict.items(), key=lambda x: x[1]) if counts_dict else (None, 0)
    )

    # Calculate entropy
    entropy = calculate_shannon_entropy(list(probs.values())) if probs else 0

    # Perform uniformity test
    uniformity_test = test_uniform_distribution(counts_dict)

    # Build comprehensive analysis result
    result = {
        "counts": dict(counts_dict),
        "probabilities": probs,
        "total_observations": total,
        "most_common": {
            "label": most_common[0],
            "count": most_common[1],
            "probability": probs.get(most_common[0], 0) if most_common[0] else 0,
        },
        "least_common": {
            "label": least_common[0],
            "count": least_common[1],
            "probability": probs.get(least_common[0], 0) if least_common[0] else 0,
        },
        "entropy": entropy,
        "uniformity_test": uniformity_test,
    }

    return result
