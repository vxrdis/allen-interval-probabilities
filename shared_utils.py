"""
Shared Utility Functions for Allen's Interval Algebra

This module provides common helper functions used across the Allen interval
algebra implementation, including:

1. Statistical functions (entropy calculation, normalization)
2. Visualization helpers
3. Data transformation utilities

These utilities ensure consistent implementations across the visualization modules.
"""

import numpy as np
from scipy.stats import entropy as scipy_entropy


def calculate_shannon_entropy(distribution):
    """
    Calculate Shannon entropy of a probability distribution.

    Args:
        distribution: List or dictionary of probabilities

    Returns:
        Entropy value (higher means more uncertainty)
    """
    # If passed a dictionary, extract values
    if isinstance(distribution, dict):
        distribution = list(distribution.values())

    # Make sure the distribution is normalized and contains no zeros
    distribution = np.array(distribution)
    distribution = distribution[distribution > 0]
    if len(distribution) == 0:
        return 0

    distribution = distribution / np.sum(distribution)
    return scipy_entropy(distribution, base=2)


def normalize_counts(counts):
    """
    Normalize a dictionary or list of counts to probabilities.

    Args:
        counts: Dictionary or list of counts

    Returns:
        Dictionary or list of normalized probabilities
    """
    if isinstance(counts, dict):
        total = sum(counts.values())
        if total > 0:
            return {key: value / total for key, value in counts.items()}
        return {key: 0 for key in counts}
    else:
        # For lists/arrays
        total = sum(counts)
        if total > 0:
            return [value / total for value in counts]
        return [0] * len(counts)


def uniform_distribution_value(n_categories):
    """
    Return the probability value for a uniform distribution.

    Args:
        n_categories: Number of categories in the distribution

    Returns:
        The uniform probability value (1/n)
    """
    return 1.0 / n_categories
