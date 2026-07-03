# wheel.py serves as the evolution loop, altering with each change in the adaptation
# proves the genome's adaptation success by re-testing all phenomena against the evolved winner with zero fitness degradation.

import neat 
from adaptative_genome import AdaptativeGenome
from phenomena import PhenomenonRegistry, XORPhenomenon, SequenceMemoryPhenomenon, GaussianApproxPhenomenon
from fitness import MultiPhenomenaEvaluator
import time 

# Wheel serves as a way to signify that the adaptation was reached
class AdaptationWheel:
    def __init__(self, config_path):
        self.config = neat.Config(AdaptativeGenome,
            neat.DefaultReproduction,
            neat.DefaultSpeciesSet,
            neat.DefaultStagnation,
            config_path
        )
        self.registry = PhenomenonRegistry()
        self.adaptation_log = []
        self.topology_history=[]
        
        self.winner=None
    
    def setup_phenomena(self):
        self.registry.register(XORPhenomenon())
        self.registry.register(SequenceMemoryPhenomenon())
        self.registry.register(GaussianApproxPhenomenon())
    
    def run_adaptation_cycle(self, phenomenon_id, max_generations=150):
        
        """Evolve the population until it is adapted to the current phenomenon"""
        evaluator = MultiPhenomenaEvaluator(self.registry, self.config)
        population = neat.Population(self.config)

        """
        Record generations+adaptation state and evaluate the best genome of this generation 
        and its topology through a nested function, as to prevent interferene from global variables. 
        Structural changes will be recorded for this phenomenon, after which the winner will be assigned
        """

        generation_count = 0
        adapted = False
        #############################################

        def eval_genomes(genomes, config):
            nonlocal generation_count, adapted 
            evaluator.evaluate_genomes(genomes, config)
            generation_count += 1
            best_genome = max (( g for _, g in genomes), key=lambda g: g.fitness)
            nodes, conns = best_genome.get_complexity()
            self.topology_history.append({
                "generation": len(self.topology_history),
                "nodes": nodes,
                "connections": conns,
                # track by innovation/phenomenon no.
                "phenomenon": phenomenon_id,
                "fitness": best_genome.fitness,
            })
            if self.registry.all_adapted(): 
                adapted = True

         ########################################   
        winner = population.run(eval_genomes, max_generations)

        if hasattr(winner, "record_adaptation"):
            winner.record_adaptation(phenomenon_id)

        self.champion = winner
        self.adaptation_log.append({
            "phenomenon": phenomenon_id,
            "generations": generation_count,
            "adapted": adapted or 
    self.registry.is_adapted(phenomenon_id),
            "final_fitness": winner.fitness,
            "complexity": winner.get_complexity(),
        })
        return winner, evaluator.generation_stats
    
    """ 
    Prove the system works through an immunity verifican function.
    the winner is retested with a fresh recurrent network, 
    once its topology has adapted to all phenomena, to verify
    whether that the fitness does not degrade
    """
    def verify_immunity(self):
        if self.champion is None:
            return {}
        
        network = neat.nn.RecurrentNetwork.create(self.champion,
                                                  self.config)
        immunity_results = {}

        for pid in self.registry.exposure_order:
            phenomenon = self.registry.phenomena[pid]
            score = phenomenon.evaluate(network)
            immunity_results[pid] = score
        
        return immunity_results
    
    """
    Orchestration method - loop iterates through phenomena in registration order. 
    Thep population must maintain fitness, without any stagnation. If it fails to adapt and
    reach a fitness threshold of 0.85 (as set in neat_config.ini) within 150 generations 
    (max_generations) the adaptation cycle ends. 
    """

    def run_full_adaptation(self):
        self.setup_phenomena()
        all_stats = {}

        for pid in self.registry.exposure_order:
            print(f"\n{'='*60}")
            print(f"BEGINNING ENCOUNTER.")
            time.sleep(5)
            print(f"Encountering '{self.registry.phenomena[pid].name}'. THE WHEEL TURNS")
            print(f"{'='*60}") 
            print(f"Active phenomena:{len(self.registry.get_encountered_phenomena())}")
            
            winner, stats = self.run_adaptation_cycle(pid)
            all_stats[pid] = stats

            nodes, conns = winner.get_complexity()
            print(f"Adaptation complete. Topology: {nodes} nodes, {conns} connections")
            print(f"Fitness: {winner.fitness:.4f}")
            
            print(f"\n{'='*60}")
            print("IMMUNITY VERIFICATION: Re-testing all phenomena")
            print(f"{'='*60}")

            immunity = self.verify_immunity()
            for pid, score in immunity.items():
             name = self.registry.phenomena[pid].name
             status = "IMMUNE" if score >= self.registry.adaptation_threshold else "VULNERABLE"
             print(f"  {name}: {score:.4f} [{status}]")

             return all_stats, immunity
            
          