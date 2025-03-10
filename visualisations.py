"""
Advanced Visualisations for Allen's Interval Algebra Simulations

This module provides specialised visualisation functions for analysing simulation data
from Allen's interval algebra. It generates informative plots to help understand the
distribution of interval relations and their compositions under different parameters.

The visualisations use Alspaugh's notation for the 13 Allen relations:
p: Before        M: Met-by
m: Meets         O: Overlapped-by
o: Overlaps      f: Finishes
F: Finished-by   d: During
D: Contains      S: Started-by
s: Starts        P: After
e: Equals

All plots follow the standard order: p, m, o, F, D, s, e, S, d, f, O, M, P
"""

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import seaborn as sns
from scipy.stats import entropy
import pandas as pd
from matplotlib.colors import LinearSegmentedColormap
import os
import time

# Import from our modules
from relations import ALLEN_RELATION_ORDER, get_relation_name, compose_relations
from simulations import arSimulate, simulateRed, tallyProb
import simulations

# Create output directory if it doesn't exist
os.makedirs("visualisations", exist_ok=True)

# Define colour schemes
RELATION_COLOURS = {
    "p": "#1f77b4",  # blue
    "m": "#ff7f0e",  # orange
    "o": "#2ca02c",  # green
    "F": "#d62728",  # red
    "D": "#9467bd",  # purple
    "s": "#8c564b",  # brown
    "e": "#e377c2",  # pink
    "S": "#7f7f7f",  # gray
    "d": "#bcbd22",  # olive
    "f": "#17becf",  # cyan
    "O": "#aec7e8",  # light blue
    "M": "#ffbb78",  # light orange
    "P": "#98df8a",  # light green
}


def calculate_shannon_entropy(distribution):
    """
    Calculate Shannon entropy of a probability distribution.

    Args:
        distribution: List of probabilities

    Returns:
        Entropy value (higher means more uncertainty)
    """
    # Make sure the distribution is normalised and contains no zeros
    distribution = np.array(distribution)
    distribution = distribution[distribution > 0]
    if len(distribution) == 0:
        return 0
    distribution = distribution / np.sum(distribution)
    return entropy(distribution, base=2)


def plot_relation_distribution(distribution, title, filename=None, show_uniform=True):
    """
    Plot the distribution of Allen relations as a bar chart.

    Args:
        distribution: Dictionary mapping relation codes to frequencies or probabilities
        title: Title for the plot
        filename: If provided, save the plot to this filename
        show_uniform: Whether to show the line for uniform distribution (1/13)

    Returns:
        The figure and axes objects
    """
    # Create figure with decent size
    fig, ax = plt.subplots(figsize=(14, 8))

    # Extract data in the fixed order
    relations = ALLEN_RELATION_ORDER
    values = [distribution[rel] for rel in relations]

    # Create bar chart with custom colours - Note: matplotlib requires American spelling for parameters
    bars = ax.bar(relations, values, color=[RELATION_COLOURS[rel] for rel in relations])

    # Add uniform distribution line if requested
    if show_uniform:
        ax.axhline(
            y=1 / 13, color="red", linestyle="--", label="Uniform distribution (1/13)"
        )
        ax.legend(fontsize=12)

    # Add labels and title
    ax.set_xlabel("Allen Relations", fontsize=14)
    ax.set_ylabel("Probability", fontsize=14)
    ax.set_title(title, fontsize=16)

    # Add relation names as text annotations
    for i, rel in enumerate(relations):
        name = get_relation_name(rel)
        ax.text(
            i,
            values[i] + 0.005,
            name,
            ha="center",
            rotation=90,
            fontsize=10,
            color="darkblue",
        )

    # Add grid for easier reading
    ax.grid(axis="y", linestyle="--", alpha=0.7)

    # Tight layout for better use of space
    plt.tight_layout()

    # Save the plot if filename is provided
    if filename:
        plt.savefig(f"visualisations/{filename}", dpi=300, bbox_inches="tight")
        print(f"Distribution plot saved as 'visualisations/{filename}'")

    return fig, ax


def create_composition_matrix():
    """
    Create a theoretical composition matrix based on Allen's interval algebra.

    Returns:
        A 13×13 NumPy array where cell [i, j] contains the list of possible
        relations when composing relations in positions i and j in ALLEN_RELATION_ORDER
    """
    n = len(ALLEN_RELATION_ORDER)
    matrix = np.empty((n, n), dtype=object)

    for i, rel1 in enumerate(ALLEN_RELATION_ORDER):
        for j, rel2 in enumerate(ALLEN_RELATION_ORDER):
            matrix[i, j] = compose_relations(rel1, rel2)

    return matrix


def plot_composition_heatmap_entropy(matrix, title, filename=None):
    """
    Generate a heatmap of the composition table, showing entropy for each cell.

    Args:
        matrix: A 13×13 matrix where each cell is a list of possible relations
        title: Title for the plot
        filename: If provided, save the plot to this filename

    Returns:
        The figure and axes objects
    """
    n = len(ALLEN_RELATION_ORDER)

    # Calculate entropy for each cell
    entropy_matrix = np.zeros((n, n))
    for i in range(n):
        for j in range(n):
            # Count how many relations in each cell and calculate entropy
            # Assuming equal probability for each possible relation in a cell
            num_relations = len(matrix[i, j])
            if num_relations > 0:
                probs = [1 / num_relations] * num_relations
                entropy_matrix[i, j] = calculate_shannon_entropy(probs)

    # Create a DataFrame for better axis labelling
    df = pd.DataFrame(
        entropy_matrix, index=ALLEN_RELATION_ORDER, columns=ALLEN_RELATION_ORDER
    )

    # Create figure with suitable size
    plt.figure(figsize=(14, 12))

    # Custom colourmap from blue (low entropy) to red (high entropy)
    cmap = LinearSegmentedColormap.from_list(
        "entropy_cmap", ["#1a9850", "#ffffbf", "#d73027"], N=256
    )

    # Generate heatmap
    ax = sns.heatmap(
        df,
        annot=True,
        cmap=cmap,
        fmt=".2f",
        linewidths=0.5,
        cbar_kws={"label": "Shannon Entropy (bits)"},
    )

    # Add cell annotations showing the possible relations
    for i in range(n):
        for j in range(n):
            relations_text = ",".join(matrix[i, j])
            text_colour = "black" if entropy_matrix[i, j] < 2 else "white"
            ax.text(
                j + 0.5,
                i + 0.5,
                relations_text,
                ha="center",
                va="center",
                fontsize=7,
                color=text_colour,
            )

    # Add labels and title
    ax.set_title(title, fontsize=16, pad=20)
    ax.set_xlabel("Second Relation (rel₂)", fontsize=14)
    ax.set_ylabel("First Relation (rel₁)", fontsize=14)

    # Adjust layout
    plt.tight_layout()

    # Save the plot if filename is provided
    if filename:
        plt.savefig(f"visualisations/{filename}", dpi=300, bbox_inches="tight")
        print(f"Composition heatmap saved as 'visualisations/{filename}'")

    return plt.gcf(), ax


def plot_composition_heatmap_size(matrix, title, filename=None):
    """
    Generate a heatmap showing the number of possible relations for each composition.

    Args:
        matrix: A 13×13 matrix where each cell is a list of possible relations
        title: Title for the plot
        filename: If provided, save the plot to this filename

    Returns:
        The figure and axes objects
    """
    n = len(ALLEN_RELATION_ORDER)

    # Calculate cardinality for each cell
    cardinality_matrix = np.zeros((n, n))
    for i in range(n):
        for j in range(n):
            cardinality_matrix[i, j] = len(matrix[i, j])

    # Create a DataFrame for better axis labelling
    df = pd.DataFrame(
        cardinality_matrix, index=ALLEN_RELATION_ORDER, columns=ALLEN_RELATION_ORDER
    )

    # Create figure with suitable size
    plt.figure(figsize=(14, 12))

    # Generate heatmap
    ax = sns.heatmap(
        df,
        annot=True,
        cmap="YlGnBu",
        fmt=".0f",
        linewidths=0.5,
        cbar_kws={"label": "Number of possible relations"},
    )

    # Add cell annotations showing the possible relations
    for i in range(n):
        for j in range(n):
            relations_text = ",".join(matrix[i, j])
            ax.text(
                j + 0.5,
                i + 0.85,
                relations_text,
                ha="center",
                va="center",
                fontsize=7,
                color="black",
            )

    # Add labels and title
    ax.set_title(title, fontsize=16, pad=20)
    ax.set_xlabel("Second Relation (rel₂)", fontsize=14)
    ax.set_ylabel("First Relation (rel₁)", fontsize=14)

    # Adjust layout
    plt.tight_layout()

    # Save the plot if filename is provided
    if filename:
        plt.savefig(f"visualisations/{filename}", dpi=300, bbox_inches="tight")
        print(f"Composition size heatmap saved as 'visualisations/{filename}'")

    return plt.gcf(), ax


def plot_empirical_composition_heatmap(tally_dict, title, filename=None):
    """
    Generate a heatmap showing empirical composition probabilities from simulation data.

    Args:
        tally_dict: Dictionary with composition tallies
        title: Title for the plot
        filename: If provided, save the plot to this filename

    Returns:
        The figure and axes objects
    """
    n = len(ALLEN_RELATION_ORDER)

    # Initialise the matrix with zeros
    freq_matrix = np.zeros((n, n, n))  # [rel1, rel2, result]

    # Populate matrix from tally dictionary
    for i, rel1 in enumerate(ALLEN_RELATION_ORDER):
        for j, rel2 in enumerate(ALLEN_RELATION_ORDER):
            key = f"{rel1},{rel2}"
            if key in tally_dict:
                for k, rel3 in enumerate(ALLEN_RELATION_ORDER):
                    if rel3 in tally_dict[key]:
                        freq_matrix[i, j, k] = tally_dict[key][rel3]

    # Create a DataFrame for the most common result in each cell
    most_common = np.zeros((n, n))
    for i in range(n):
        for j in range(n):
            if np.sum(freq_matrix[i, j]) > 0:
                most_common[i, j] = np.argmax(freq_matrix[i, j])

    df = pd.DataFrame(
        most_common, index=ALLEN_RELATION_ORDER, columns=ALLEN_RELATION_ORDER
    )

    # Create figure with suitable size
    plt.figure(figsize=(14, 12))

    # Generate heatmap
    cmap = plt.cm.get_cmap("tab20", n)
    ax = sns.heatmap(
        df,
        cmap=cmap,
        linewidths=0.5,
        cbar_kws={"label": "Most common resulting relation"},
    )

    # Add cell annotations
    for i in range(n):
        for j in range(n):
            cell_sum = np.sum(freq_matrix[i, j])
            if cell_sum > 0:
                # Find the most common relation and its percentage
                idx = int(most_common[i, j])
                rel = ALLEN_RELATION_ORDER[idx]
                pct = freq_matrix[i, j, idx] / cell_sum * 100

                # Add text showing the most common relation and its percentage
                ax.text(
                    j + 0.5,
                    i + 0.5,
                    f"{rel}\n{pct:.1f}%",
                    ha="center",
                    va="center",
                    fontsize=9,
                    color="black" if idx < n / 2 else "white",
                )

    # Add labels and title
    ax.set_title(title, fontsize=16, pad=20)
    ax.set_xlabel("Second Relation (rel₂)", fontsize=14)
    ax.set_ylabel("First Relation (rel₁)", fontsize=14)

    # Create a custom colourbar with relation labels
    cbar = ax.collections[0].colorbar
    cbar.set_ticks(np.arange(0.5, n))
    cbar.set_ticklabels(ALLEN_RELATION_ORDER)

    # Adjust layout
    plt.tight_layout()

    # Save the plot if filename is provided
    if filename:
        plt.savefig(f"visualisations/{filename}", dpi=300, bbox_inches="tight")
        print(f"Empirical composition heatmap saved as 'visualisations/{filename}'")

    return plt.gcf(), ax


def animate_distribution_evolution(pBorn, pDie, max_trials=10000, step_size=500):
    """
    Create an animation showing how relation distributions evolve as trials increase.

    Args:
        pBorn: Birth probability
        pDie: Death probability
        max_trials: Maximum number of trials to simulate
        step_size: Number of trials to add in each animation frame

    Returns:
        The animation object
    """
    fig, ax = plt.subplots(figsize=(14, 8))

    # Initialise bar chart
    relations = ALLEN_RELATION_ORDER
    bars = ax.bar(
        relations,
        [0] * len(relations),
        color=[RELATION_COLOURS[rel] for rel in relations],
    )

    # Add uniform distribution line
    ax.axhline(y=1 / 13, color="red", linestyle="--", label="Uniform (1/13)")
    ax.legend()

    # Set labels and title
    ax.set_xlabel("Allen Relations", fontsize=14)
    ax.set_ylabel("Probability", fontsize=14)
    title = ax.set_title(
        f"Evolution of Relation Probabilities (pBorn={pBorn}, pDie={pDie})\nTrials: 0",
        fontsize=16,
    )

    # Set y-axis limit
    ax.set_ylim(0, 0.3)  # Adjust based on expected values

    # Text for displaying time elapsed
    time_text = ax.text(0.02, 0.95, "", transform=ax.transAxes)

    # Initialise counts
    aggregated_counts = {rel: 0 for rel in relations}

    def update(frame):
        # Time the simulation
        start_time = time.time()

        # Run simulation for this step
        new_runs = simulateRed(pBorn, pDie, step_size)

        # Update aggregated counts
        for run in new_runs:
            rel_code = simulations.arCode(run)
            if rel_code:
                aggregated_counts[rel_code] += 1

        # Calculate probabilities
        total = sum(aggregated_counts.values())
        probabilities = [
            aggregated_counts[rel] / total if total > 0 else 0 for rel in relations
        ]

        # Update bars
        for bar, h in zip(bars, probabilities):
            bar.set_height(h)

        # Update title and time text
        title.set_text(
            f"Evolution of Relation Probabilities (pBorn={pBorn}, pDie={pDie})\nTrials: {(frame+1)*step_size}"
        )
        elapsed = time.time() - start_time
        time_text.set_text(f"Time for {step_size} trials: {elapsed:.2f}s")

        return bars

    # Create animation
    frames = max_trials // step_size
    ani = animation.FuncAnimation(fig, update, frames=frames, interval=200, blit=False)

    # Save animation
    filename = f"visualisations/evolution_{pBorn}_{pDie}.mp4"
    ani.save(filename, writer="ffmpeg", fps=5, dpi=200)
    print(f"Animation saved as '{filename}'")

    return ani


def generate_probability_tables(prob_ranges, trial_count=5000):
    """
    Generate a set of visualisations for different birth/death probability combinations.

    Args:
        prob_ranges: List of probability values to try
        trial_count: Number of trials for each simulation
    """
    print(f"Generating probability tables for {len(prob_ranges)^2} combinations...")

    results = {}

    # Run simulations for all combinations
    for pBorn in prob_ranges:
        for pDie in prob_ranges:
            print(f"Simulating with pBorn={pBorn}, pDie={pDie}...")
            dic = arSimulate(pBorn, pDie, trial_count)

            # Normalise to get probabilities
            total = sum(dic.values())
            probs = {rel: dic[rel] / total for rel in ALLEN_RELATION_ORDER}

            # Store results
            key = f"{pBorn},{pDie}"
            results[key] = probs

            # Generate visualisation
            title = f"Allen Relation Distribution (pBorn={pBorn}, pDie={pDie})"
            filename = f"distribution_{pBorn}_{pDie}.png"
            plot_relation_distribution(probs, title, filename)

    # Create a heatmap showing the most common relation for each probability combination
    most_common_matrix = np.zeros((len(prob_ranges), len(prob_ranges)), dtype=int)
    for i, pBorn in enumerate(prob_ranges):
        for j, pDie in enumerate(prob_ranges):
            key = f"{pBorn},{pDie}"
            probs = results[key]
            most_common_rel = max(probs, key=probs.get)
            most_common_idx = ALLEN_RELATION_ORDER.index(most_common_rel)
            most_common_matrix[i, j] = most_common_idx

    # Create heatmap for most common relation
    plt.figure(figsize=(12, 10))
    df = pd.DataFrame(most_common_matrix, index=prob_ranges, columns=prob_ranges)

    cmap = plt.cm.get_cmap("tab20", len(ALLEN_RELATION_ORDER))
    ax = sns.heatmap(df, cmap=cmap, linewidths=0.5)

    # Add annotations
    for i in range(len(prob_ranges)):
        for j in range(len(prob_ranges)):
            idx = most_common_matrix[i, j]
            rel = ALLEN_RELATION_ORDER[idx]
            ax.text(
                j + 0.5,
                i + 0.5,
                rel,
                ha="center",
                va="center",
                fontsize=12,
                color="black" if idx < len(ALLEN_RELATION_ORDER) / 2 else "white",
            )

    plt.title("Most Common Allen Relation by Birth/Death Probability", fontsize=16)
    plt.xlabel("Death Probability (pDie)", fontsize=14)
    plt.ylabel("Birth Probability (pBorn)", fontsize=14)

    # Create custom colourbar with relation labels
    cbar = ax.collections[0].colorbar
    cbar.set_ticks(np.arange(0.5, len(ALLEN_RELATION_ORDER)))
    cbar.set_ticklabels(ALLEN_RELATION_ORDER)

    # Save the heatmap
    plt.tight_layout()
    plt.savefig(
        "visualisations/most_common_relation_heatmap.png", dpi=300, bbox_inches="tight"
    )
    print(
        "Most common relation heatmap saved as 'visualisations/most_common_relation_heatmap.png'"
    )


if __name__ == "__main__":
    print("Generating Allen's Interval Algebra visualisations...")

    # Generate basic distribution visualisation for a specific simulation
    print("\nSimulating distribution for pBorn=0.1, pDie=0.1...")
    dist = arSimulate(0.1, 0.1, 10000)
    total = sum(dist.values())
    probs = {rel: dist[rel] / total for rel in dist}

    plot_relation_distribution(
        probs,
        "Allen Relation Distribution (pBorn=0.1, pDie=0.1, 10,000 trials)",
        "basic_distribution.png",
    )

    # Generate composition matrix visualisation
    print("\nGenerating composition matrix visualisation...")
    matrix = create_composition_matrix()

    plot_composition_heatmap_entropy(
        matrix, "Allen Relation Composition Table - Entropy", "composition_entropy.png"
    )

    plot_composition_heatmap_size(
        matrix,
        "Allen Relation Composition Table - Number of Possible Relations",
        "composition_size.png",
    )

    # Generate visualisations for different probability combinations
    print("\nGenerating visualisations for different probability combinations...")
    prob_ranges = [0.01, 0.05, 0.1, 0.2, 0.5]

    # Comment out if time-consuming
    # generate_probability_tables(prob_ranges, 5000)

    # Create animation for a specific case
    # Uncomment if you want to generate animation (can be time-consuming)
    # print("\nCreating animation of distribution evolution...")
    # animate_distribution_evolution(0.1, 0.1, 5000, 500)

    print("\nVisualisation generation complete!")
    print(f"All visualisations saved in the 'visualisations/' directory.")
