# main.py
""" 
Main Script 
 - Main entry point for the adaptive neuroevolution engine.
 - Initializes the adaptation wheel class
 - Runs the full adaptation loop, generating visualizations of topology growth and immunity heatmap, and prints a final adaptation report showing champion topology, adaptation registry, wheel state progress and immunity verification
 - 
"""

"""The Wheel Turns: Adaptive Neuroevolution Against Categorical Phenomena"""

import os
from wheel import AdaptationWheel
from visualize import plot_topology_growth, plot_immunity_heatmap
import pygame 

pygame.mixer.init()
pygame.mixer.music.load("sfx.mp3")


def main():
    # Locate the NEAT config file relative to this script
    config_path = os.path.join(os.path.dirname(__file__), "neat_config.ini")
    print("=" * 60)
    print("Adaptive Neuroevolution Engine: Wheel State Progression")
    print("=" * 60)
    print()
    print("Phenomena to adapt to:")
    print("  1. XOR Boolean Logic (requires hidden nodes)")
    print("  2. Temporal Sequence Memory (requires recurrent connections)")
    print("  3. Gaussian Approximation (requires diverse activation topology)")
    print()

    # Run the full adaptation loop across all phenomena
    wheel = AdaptationWheel(config_path)
    all_stats, immunity = wheel.run_full_adaptation()


    # Generate visualization PNGs
    print(f"\n{'='*60}")
    print("GENERATING VISUALIZATIONS")
    print(f"{'='*60}")
    plot_topology_growth(wheel.topology_history)
    plot_immunity_heatmap(all_stats, wheel.registry)
    # Print the final adaptation report
    print(f"\n{'='*60}")
    print("ADAPTATION REPORT")
    print(f"{'='*60}")
    if wheel.champion:
        nodes, conns = wheel.champion.get_complexity()
        print(f"Champion topology: {nodes} nodes, {conns} connections")
        print(f"Champion fitness: {wheel.champion.fitness:.4f}")
        if hasattr(wheel.champion, "adaptation_history"):
            print("\nAdaptation Registry:")
            for pid, adaptations in wheel.champion.adaptation_history.items():
                name = wheel.registry.phenomena[pid].name
                print(f"  {name}: {len(adaptations)} structural innovations")
    # Print wheel state progress bars
    print("\nWheel State (final):")
    for pid, progress in wheel.registry.adaptation_state.items():
        name = wheel.registry.phenomena[pid].name
        bar = "#" * int(progress * 20) + "-" * (20 - int(progress * 20))
        print(f"  {name}: [{bar}] {progress:.2f}")
    # Immunity verification summary
    print("\nImmunity Verification:")
    all_immune = True
    for pid, score in immunity.items():
        name = wheel.registry.phenomena[pid].name
        immune = score >= wheel.registry.adaptation_threshold
        if not immune:
            all_immune = False
        symbol = "[IMMUNE]" if immune else "[VULNERABLE]"
        print(f"  {name}: {score:.4f} {symbol}")
    if all_immune:
        pygame.mixer.music.play()
        print("\n>>> ALL PHENOMENA ADAPTED. THE WHEEL HAS TURNED. <<<")
        while pygame.mixer.music.get_busy():
            pygame.time.Clock().tick(10)
    else:
        print("\n>>> ADAPTATION INCOMPLETE. MORE GENERATIONS REQUIRED. <<<")


if __name__ == "__main__":
    main()