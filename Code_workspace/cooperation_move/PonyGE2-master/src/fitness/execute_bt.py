from base_ff_classes.base_ff import base_ff
from ..py_trees_interface import PyTree

class execute_bt(base_ff):
    """Fitness function for behaviour tree"""
    def __init__(self):
        # Initialise base fitness function class
        super().__init__()

    def evaluate(self, ind, **kwargs):
        execute_behaviour = PyTree(ind.phenotype)
        # run the Behavior Tree
        fitness = execute_behaviour.tick_bt()
        return fitness