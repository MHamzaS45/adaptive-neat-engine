######################################
# References for Theory
# "Neuroevolution of Augmenting Topologies" (NEAT) by Stanley and Miikkulainen (2002)
#######################################

import math
import random

# abstraction
class Phenomenon: 

    """
    Base class for every and all phenomena, each defines a problem that
    requires specific structural features in a neural network to adapt to.
    """

    def __init__(self, phenomenon_id, name, structural_requirement):
        self.phenomenon_id = phenomenon_id
        self.name = name
        self.structural_requirement = structural_requirement

    def evaluate(self, network):
        """
        Evaluate the networks performance against the phenomnon via fitness
        function, through measuring squared error and inverting it to achieve a
        higher fitness score.
        """
        raise NotImplementedError
    
    def get_result_pairs(self):
        """ 
        Receive input/output pairs
        """
        raise NotImplementedError

# input to output network phenomenon with hidden node    
class XORPhenomenon(Phenomenon): 
    def __init__(self):
        super().__init__(
            phenomenon_id="boolean_logic",
            name="XOR Boolean Logic",
            structural_requirement="hidden_nodes" # impossible to exist without growing the hidden topology
        )

    def get_result_pairs(self):
     """
     XOR Table
     """
     return [
        ([0.0, 0.0], [0.0]),
        ([0.0, 1.0], [1.0]),
        ([1.0, 0.0], [1.0]),
        ([1.0, 1.0], [0.0])
    ]

    def evaluate(self, network):
        test_cases = self.get_result_pairs()
        total_error = 0.0
        for inputs, expected in test_cases:
            output = network.activate(inputs)
            total_error += (output[0] - expected[0]) ** 2

            # fitness is inverse of error, normalized to 0.0-1.0
            max_error = len(test_cases) * 1.0
            fitness = 1.0 - (total_error / max_error)
            return max(0.0, fitness)

# memory phenomenon (recurrent network)
class SequenceMemoryPhenomenon(Phenomenon):
    """Recurrent network phenomenon that requires
     memory to solve sequence prediction problems."""
    
    def __init__(self):
        super().__init__(
            phenomenon_id="sequence_memory",
            name="Sequence Memory",
            structural_requirement="recurrent_connections" # requires recurrent connections to maintain state across time steps
        )
        self.sequence_length = 8
        random.seed(42) 
        # determinism
        self.sequence = [round(random.random(), 1) for 
                         _ in range(self.sequence_length)]
    
    def get_result_pairs(self):
        cases = []
        for i in range(self.sequence_length - 1):
            current_input = [self.sequence[i]]
            if i == 0:
                expected_output = [0.0]
            else:
                expected_output = [self.sequence[i - 1]]
                cases.append((current_input, expected_output))
                
        return cases
    
    def evaluate(self, network):
        """ clear recurrent state to prevent
        contamination from previous runs"""

        network.reset() 
        test_cases = self.get_result_pairs()
        total_error = 0.0
        for inputs, expected in test_cases:
            # Network expects 2 inputs, but the phenomenon only provides 1. 
            padded_inputs = inputs + [0.0] if len(inputs) < 2 else inputs
            output = network.activate(padded_inputs)
            total_error += (output[0] - expected[0]) ** 2 
        max_error = len(test_cases) * 1.0 
        fitness = 1.0 - (total_error / max_error)
        return max(0.0, fitness)
    
# For networks that represent both a rise and fall of the curve
class GaussianApproxPhenomenon(Phenomenon):
    """Multiple hidden nodes with diverse activation
    functions. """

    def __init__(self):
        super().__init__( 
            phenomenon_id="gaussian_approx",
            name="Gaussian Approximation",
            structural_requirement="diverse_hidden_topology"
        )
        self.num_samples = 20
        """ Generating 20 evenly spaced points
        between -3.0 and 3.0."""
        self.test_points = [ -3.0 + (6.0 * i / (self.num_samples - 1))
                            for i in range(self.num_samples) ]

    def get_result_pairs(self):
        cases = []
        for X in self.test_points:
            """ normalize input to small input ranges of 
                -1.0 to 1.0 to improve
                performance
            """
            input_val = [X / 3.0] 

            """ standard gaussian function:
                f(x) = exp(-0.5 * x^2)    """
            expected_output = [math.exp(-0.5 * (X ** 2))]
            cases.append((input_val, expected_output))
        return cases
    
    def evaluate(self, network):
        network.reset()
        test_cases = self.get_result_pairs()
        total_error = 0.0
        for inputs, expected in test_cases:
            # Network expects 2 inputs, but the phenomenon only provides 1. 
            padded_inputs = inputs + [0.0] if len(inputs) < 2 else inputs
            output = network.activate(padded_inputs)

            # Clip output to 0.0 to 1.0 range
            clipped_output = max(0.0, min(1.0, output[0]))
            total_error += (clipped_output - expected[0]) ** 2 
        
        max_error = len(test_cases) * 1.0
        fitness = 1.0 - (total_error / max_error)
        return max(0.0, fitness)
            

class PhenomenonRegistry:
    #Track all phenomena and their adaptation state.

    def __init__(self):
        self.phenomena = {}
        self.adaptation_state = {}
        # Preserve the sequence of exposure 
        self.exposure_order = []
        self.adaptation_threshold = 0.86  # Threshold for adaptation
    
    def register(self, phenomenon):
        self.phenomena[phenomenon.phenomenon_id] = phenomenon
        self.adaptation_state[phenomenon.phenomenon_id] = 0.0 
        self.exposure_order.append(phenomenon.phenomenon_id)

    def get_encountered_phenomena(self):
        return [self.phenomena[pid] for pid in self.exposure_order]
    
    def update_adaptation_state(self, phenomenon_id, fitness): 
        self.adaptation_state[phenomenon_id] = fitness
    
    def is_adapted(self, phenomenon_id):
        # confirm that the adaptation threshold of 0.86 is met
        return self.adaptation_state.get(phenomenon_id, 0.0) >= self.adaptation_threshold
    
    def all_adapted(self):
        return all (
            self.is_adapted(pid) for pid in self.exposure_order
        )
    