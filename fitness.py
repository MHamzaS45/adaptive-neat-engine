# Multi-phenomena fitness evaluation system.
# Uses harmonic mean to prevent catastrophic forgetting.

import neat

def harmonic_mean(values):
    """Compute harmonic mean of a list of values.
    Returns 0 if any value is 0 (heavily penalizes failure on any phenomenon).
    The harmonic mean is chosen specifically because it is dominated by the
    lowest value - a network that scores 0.99 on two phenomena but 0.01 on
    the third gets a harmonic mean of ~0.03, not 0.66 (arithmetic mean).
    
    It is implemented to prevent catastrophic forgetting of adaptation states,
    as the sequential exposure loop (see wheel.py) cannot sacrifice an earlier 
    adaptation to optimize a new one, ensuring the genome's topological growth
    with adaptation to a new phenomena.
    """
    
    if not values or any(v <= 0 for v in values):
        return 0.0
    n = len(values)
    reciprocal_sum = sum(1.0 / v for v in values)
    return n / reciprocal_sum


class MultiPhenomenaEvaluator:
    """Evaluates genomes against all active phenomena simultaneously."""

    def __init__(self, phenomena_registry, genome_config):
        self.registry = phenomena_registry
        self.genome_config = genome_config
        self.generation_stats = []

    def evaluate_genomes(self, genomes, config):
        """NEAT-compatible fitness evaluation function.
        Called by neat.Population.run() each generation."""
        active_phenomena = self.registry.get_encountered_phenomena()
        best_per_phenomenon = {p.phenomenon_id: 0.0 for p in active_phenomena}

        for genome_id, genome in genomes:
            # Genotype to Phenotype step. Genome converted to NN (neat\nn\recurrent.py)
            # RecurrentNetwork chosen for providing memory """
            network = neat.nn.RecurrentNetwork.create(genome, config)

            # Evaluate against each active phenomenon
            per_phenomenon_fitness = []
            for phenomenon in active_phenomena:
                score = phenomenon.evaluate(network)
                per_phenomenon_fitness.append(score)
                if score > best_per_phenomenon[phenomenon.phenomenon_id]:
                    best_per_phenomenon[phenomenon.phenomenon_id] = score

            # Composite fitness: harmonic mean prevents forgetting
            if len(per_phenomenon_fitness) == 1:
                genome.fitness = per_phenomenon_fitness[0]
            else:
                genome.fitness = harmonic_mean(per_phenomenon_fitness)

        # Update state with best scores this generation
        for pid, score in best_per_phenomenon.items():
            self.registry.update_adaptation_state(pid, score)

        self.generation_stats.append(dict(best_per_phenomenon))


""" 
Confirm adaptation through eval pipeline:
python -c "from fitness import harmonic_mean; print('HM([0.9, 0.9, 0.1]):', harmonic_mean([0.9, 0.9, 0.1])); print('AM([0.9, 0.9, 0.1]):', sum([0.9, 0.9, 0.1])/3)"
"""