# Adaptive Genome class 
# Extends neat-python lib.'s "DefaultGenome" class
# with adaptation memory and self modifying capabilities.
# Innovations (or adaptations in this case) are tracked via ID

from neat.genome import DefaultGenome

class AdaptativeGenome(DefaultGenome):
    """ A genome that can adapt its structure during the evolutionary process. It keeps track of its adaptation history and can modify its own structure based on certain criteria'
    This will know what it is adapted to and how 
    """
    def __init__(self, key):
        super().__init__(key)
        self.adaptation_history = {} 
        self.current_phenomenon = None
        self.pre_adaptation_states = None

    # Innovation awareness: track the adaptation history of the genome
    def take_structural_adaptation(self):
        """Capture current topology state via frozenset function"""
        node_keys = frozenset(self.nodes.keys())
        conn_keys = frozenset(self.connections.keys())
        return (node_keys, conn_keys)
    
    def detect_new_adaptation(self):
        # Compare current structure with previous frozen stateshots (take_structural_adaptation() ) to detect new adaptations."""
        if self.pre_adaptation_states is None: 
            return set(),set()
        
        old_nodes, old_conns = self.pre_adaptation_states
        new_nodes = set(self.nodes.keys()) - old_nodes
        new_conns = set(self.connections.keys()) - old_conns
        return new_nodes, new_conns
    

    def record_adaptation(self, phenomenon_id):
        new_nodes, new_conns = self.detect_new_adaptation()
        adaptations = set()
        for nk in new_nodes:
            adaptations.add(("node", nk))
        for ck in new_conns: 
            adaptations.add(("connection", ck))
        if phenomenon_id not in self.adaptation_history:
            self.adaptation_history[phenomenon_id] = set()
        self.adaptation_history[phenomenon_id].update(adaptations)

    def begin_exposure(self, phenomenon_id):
        """ Begin (or a new) adaptation cycle."""
        self.current_phenomenon = phenomenon_id 
        self.pre_adaptation_states = self.take_structural_adaptation

    def configure_crossover(self, genome1, genome2, config, fitness_criterion=None):
        """ 
        Override to merge adaptation histories from both parents.
        """
        super().configure_crossover(genome1, genome2, config)
        # Merge adaptation histories from parents to offpsring
        # Hasattr added to check if parents any adaptation history to the phenomenon
        # delegate fitness criterion to the parent class if provided, else default to None as library only accepts 4 args
        if fitness_criterion is not None:
            pass
        self.adaptation_history = {}
        if hasattr(genome1, "adaptation_history"):
            for pid, adaptations in genome1.adaptation_history.items():
                self.adaptation_history[pid] = set(adaptations)
        if hasattr(genome2, "adaptation_history"):
            for pid, adaptations in genome2.adaptation_history.items():
                if pid in self.adaptation_history:
                    self.adaptation_history[pid].update(adaptations)
                else:
                    self.adaptation_history[pid] = set(adaptations)
                
    def get_complexity(self):
        """Return topology complexity metrics to track topology changes."""
        num_nodes = len(self.nodes)
        num_connections = sum(
            1 for c in self.connections.values() if c.enabled
        )
        return num_nodes, num_connections