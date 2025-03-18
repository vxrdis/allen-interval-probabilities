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


def calculate_shannon_entropy(probabilities):
    """
    Calculate the Shannon entropy of a probability distribution.

    Shannon entropy measures the average information content or uncertainty
    in a probability distribution, defined as:
    H(X) = -sum(p_i * log2(p_i)) for all probabilities p_i

    Args:
        probabilities: List or array of probability values that sum to 1

    Returns:
        Shannon entropy in bits (using log base 2)

    Raises:
        ValueError: If input is empty or probabilities don't sum to approximately 1
                   (except for the special case of all zeros)
    """
    import numpy as np

    # Convert to numpy array for efficient computation
    probs = np.array(probabilities)

    # Check for empty input
    if len(probs) == 0:
        raise ValueError("Cannot calculate entropy of an empty distribution")

    # Special case: All zeros - treat as a degenerate distribution with zero entropy
    if np.sum(probs) == 0:
        return 0.0

    # Check if probabilities sum to approximately 1 (allowing for floating-point error)
    if not np.isclose(np.sum(probs), 1.0, rtol=1e-5, atol=1e-8):
        raise ValueError(f"Probabilities must sum to 1.0, got {np.sum(probs)}")

    # Filter out zero probabilities (0 * log(0) = 0 by convention in information theory)
    # This avoids log(0) which would be -infinity
    non_zero = probs > 0

    # Special case for distributions with only one non-zero probability
    # These have zero entropy (no uncertainty)
    if np.sum(non_zero) <= 1:
        return 0.0

    # Calculate entropy using only non-zero probabilities
    filtered_probs = probs[non_zero]
    entropy = -np.sum(filtered_probs * np.log2(filtered_probs))

    return float(entropy)  # Convert from numpy type to native Python float


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
