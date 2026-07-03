# visualize.py
"""

#######################################
 Visualize the results of the structural grwoth pattern 
 that proves the topology growth through showing the node and connection
 count increase at each phenomenon introduction via a dual line axis 
 chart.
 #######################################

 Also build a heatmap to prove that the fitness never degrades
 on previously adapted phenomena 
 
"""


import matplotlib.pyplot as plt
import matplotlib.patches as mpatches


def plot_topology_growth(topology_history, output_path="topology_growth.png"):
    """Plot network complexity over generations, annotated with
    phenomenon introduction points."""
    if not topology_history:
        print("No topology history to plot.")
        return
    generations = [t["generation"] for t in topology_history]
    nodes = [t["nodes"] for t in topology_history]
    connections = [t["connections"] for t in topology_history]
    fig, ax1 = plt.subplots(figsize=(12, 6))
    color_nodes = "tab:blue"
    color_conns = "tab:orange"
    ax1.set_xlabel("Generation")
    ax1.set_ylabel("Node Count", color=color_nodes)
    ax1.plot(generations, nodes, color=color_nodes, linewidth=2, label="Nodes")
    ax1.tick_params(axis="y", labelcolor=color_nodes)
    ax2 = ax1.twinx()
    ax2.set_ylabel("Connection Count", color=color_conns)
    ax2.plot(generations, connections, color=color_conns, linewidth=2, label="Connections")
    ax2.tick_params(axis="y", labelcolor=color_conns)

    # Annotate phenomenon transitions with vertical dashed lines
    current_phenomenon = None
    colors = {"boolean_logic": "red", "temporal_memory": "green", "function_approx": "purple"}
    for t in topology_history:
        if t["phenomenon"] != current_phenomenon:
            current_phenomenon = t["phenomenon"]
            ax1.axvline(
                x=t["generation"], color=colors.get(current_phenomenon, "gray"),
                linestyle="--", alpha=0.7
            )
    # Legend showing which dashed line corresponds to which phenomenon
    patches = [
        mpatches.Patch(color="red", alpha=0.7, label="XOR Introduction"),
        mpatches.Patch(color="green", alpha=0.7, label="Sequence Memory Introduction"),
        mpatches.Patch(color="purple", alpha=0.7, label="Gaussian Approx Introduction"),
    ]
    ax1.legend(handles=patches, loc="upper left")
    plt.title("Topology Growth During Adaptive Evolution (The Wheel Turns)")
    plt.tight_layout()
    plt.savefig(output_path, dpi=150)
    plt.close()
    print(f"Topology growth plot saved to {output_path}")


def plot_immunity_heatmap(all_stats, registry, output_path="immunity_heatmap.png"):
    """Create a heatmap showing fitness per phenomenon over time.
    Once a phenomenon is adapted to, its color should remain stable
    (proving immunity)."""
    if not all_stats:
        print("No stats to plot.")
        return
    phenomenon_ids = registry.exposure_order
    phenomenon_names = [registry.phenomena[pid].name for pid in phenomenon_ids]
    # Build timeline data from all adaptation cycles
    all_generations = []
    for pid in phenomenon_ids:
        if pid in all_stats:
            for gen_stat in all_stats[pid]:
                all_generations.append(gen_stat)
    if not all_generations:
        print("No generation data to plot.")
        return
    # Create matrix: rows = phenomena, cols = generations
    matrix = []
    for pid in phenomenon_ids:
        row = []
        for gen_stat in all_generations:
            score = gen_stat.get(pid, 0.0)
            row.append(score)
        matrix.append(row)
    fig, ax = plt.subplots(figsize=(14, 4))
    im = ax.imshow(matrix, aspect="auto", cmap="RdYlGn", vmin=0, vmax=1)
    ax.set_yticks(range(len(phenomenon_names)))
    ax.set_yticklabels(phenomenon_names)
    ax.set_xlabel("Generation (across all adaptation cycles)")
    ax.set_title("Adaptation Immunity Heatmap (Green = Adapted, Red = Vulnerable)")
    plt.colorbar(im, ax=ax, label="Fitness Score")
    plt.tight_layout()
    plt.savefig(output_path, dpi=150)
    plt.close()
    print(f"Immunity heatmap saved to {output_path}")