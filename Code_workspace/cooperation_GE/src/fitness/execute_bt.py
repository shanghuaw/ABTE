import sys
import math
from fitness.base_ff_classes.base_ff import base_ff
from ge_pt_interface import PyTree

class execute_bt(base_ff):
    """Fitness function for behaviour tree"""
    def __init__(self):
        # Initialise base fitness function class
        super().__init__()

    def evaluate(self, ind, **kwargs):
        execute_behaviour = PyTree(ind.phenotype)
        # run the Behavior Tree
        execute_behaviour.tick_bt()
        if not execute_behaviour.all_missions_done:
            fitness = 10000 + execute_behaviour.add_fitness
        else:
            # fitness = execute_behaviour.time_cost / 20 + execute_behaviour.energy_cost / 1000 + math.sqrt(
            #     execute_behaviour.depth ** 2 + execute_behaviour.length ** 2)
            fitness = execute_behaviour.time_cost / 50 + execute_behaviour.path_cost / 50 + math.sqrt(
                execute_behaviour.depth ** 2 + execute_behaviour.length ** 2)
        return fitness