import sys
import math
import py_trees as pt
import custom_behaviours

CONTROL_NODES = ['Seq', 'Sel']
CLOSE_NODES = ['/Seq', '/Sel']

# 用于计算适应度
path_cost = 0
time_cost = 0.0
sim_execute_task = False

def bt_depth(str_list):
    """
    Returns depth of the bt
    """
    global CONTROL_NODES
    global CLOSE_NODES
    depth = 0
    max_depth = 0
    for i in range(len(str_list)):
        if str_list[i] in CONTROL_NODES:
            depth += 1
            max_depth = max(depth, max_depth)
        elif str_list[i] in CLOSE_NODES:
            depth -= 1
            if (depth < 0) or (depth == 0 and i is not len(str_list) - 1):
                return -1
    if depth != 0:
        return -1
    return max_depth

def bt_length(str_list):
    """
    Counts number of nodes in bt. Doesn't count up characters.
    """
    global CLOSE_NODES
    length = 0
    for node in str_list:
        if node not in CLOSE_NODES:
            length += 1
    return length

class PyTree(pt.trees.BehaviourTree):
    def __init__(self, bt_string, robot_id=-1):
        str_list = bt_string.split("_")
        self.robot_id = robot_id
        self.depth = bt_depth(str_list)
        self.length = bt_length(str_list)
        self.root, has_children = custom_behaviours.get_node_from_string(self, str_list[0])
        str_list.pop(0)

        super().__init__(root=self.root)
        if has_children:
            self.create_from_string(str_list, self.root)

        #pt.display.print_ascii_tree(self.root)
    def create_from_string(self, str_list, node):
        """
        Recursive function to generate the tree from a string
        """
        while len(str_list) > 0:
            if '/' in str_list[0]:
                str_list.pop(0)
                return node
            newnode, has_children = custom_behaviours.get_node_from_string(self, str_list[0])
            str_list.pop(0)
            if has_children:
                #Node is a control node or decorator with children - add subtree via string and then add to parent
                newnode = self.create_from_string(str_list, newnode)
                node.add_child(newnode)
            else:
                #Node is a leaf/action node - add to parent, then keep looking for siblings
                node.add_child(newnode)
        #This return is only reached if there are too few up nodes
        return node

    def tick_bt(self):
        """
        Function executing the behavior tree
        """
        max_ticks = 200
        ticks = 0
        max_fails = 1
        fails = 0
        requested_successes = 1
        successes = 0
        while (self.root.status is not pt.common.Status.FAILURE or fails < max_fails) and \
              (self.root.status is not pt.common.Status.SUCCESS or successes < requested_successes) and \
              ticks < max_ticks:
            self.root.tick_once()
            ticks += 1
            if self.root.status is pt.common.Status.SUCCESS:
                successes += 1
            else:
                successes = 0
            if self.root.status is pt.common.Status.FAILURE:
                fails += 1
        global sim_execute_task
        global path_cost
        global time_cost
        if fails > 0 or not sim_execute_task:
            fitness = sys.maxsize
        else:
            fitness = 5 * path_cost + 2 * time_cost + math.sqrt(self.depth ** 2 + self.length ** 2)
        return fitness