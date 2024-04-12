import py_trees as pt
import custom_behaviours
import ge_behaviours
from mission import mission_list

CONTROL_NODES = ['Seq', 'Sel']
CLOSE_NODES = ['/Seq', '/Sel']

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

def global_init(robot_id):
    ge_behaviours.ge_info = {
        'is_blocked_by': -1,
        'blocked': False,
        'mission_todo': -1,
        'reached': False,
        'robot_state': 'No Check',
        'move_success': False,
        'execute_success': False,
        'avoid_success': False,
        'current_location': [0, 0],
        'current_energy': ge_behaviours.INITIAL_ENERGY,
        'total_path_cost': 0,
        'total_time_cost': 0.0,
        'total_score': 0.0,
        'accomplished_missions': list(),
        'mission_counts': 0,
        'is_mission': [False, False, False]
    }
    for i in custom_behaviours.allocated_missions[robot_id]:
        mission_list[i].state = 'Idle'

class PyTree(pt.trees.BehaviourTree):
    def __init__(self, bt_string):
        self.robot_id = custom_behaviours.current_GE_robot
        global_init(self.robot_id)  # 每个行为树对象都需要初始化全局变量
        str_list = bt_string.split("_")
        self.bt_string = bt_string
        self.time_cost = 0
        self.path_cost = 0
        self.energy_cost = 0
        self.add_fitness = 0
        self.all_missions_done = False
        self.depth = bt_depth(str_list)
        self.length = bt_length(str_list)
        self.root, has_children = ge_behaviours.get_node_from_string(self, str_list[0])
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
            newnode, has_children = ge_behaviours.get_node_from_string(self, str_list[0])
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
        max_fails = 100
        fails = 0
        requested_successes = len(custom_behaviours.allocated_missions[self.robot_id])
        successes = 0
        while (self.root.status is not pt.common.Status.FAILURE or fails < max_fails) and \
              (self.root.status is not pt.common.Status.SUCCESS or successes < requested_successes) and \
              ticks < max_ticks:
            self.root.tick_once()
            ticks += 1
            if self.root.status is pt.common.Status.SUCCESS:
                successes += 1
            if self.root.status is pt.common.Status.FAILURE:
                fails += 1
        self.time_cost = ge_behaviours.ge_info['total_time_cost']
        self.path_cost = ge_behaviours.ge_info['total_path_cost']
        self.energy_cost = ge_behaviours.INITIAL_ENERGY - ge_behaviours.ge_info['current_energy']
        # if ge_behaviours.ge_info['execute_success']:
        # print("robot{} bt string:{}".format(self.robot_id, self.bt_string))
        # print("requested_successes:{}, successes:{}, fails:{}, ticks:{}".format(
        #     requested_successes, successes, fails, ticks))
        # print("accomplished:", ge_behaviours.ge_info['accomplished_missions'])
        if len(ge_behaviours.ge_info['accomplished_missions']) == \
                len(custom_behaviours.allocated_missions[self.robot_id]) and \
                successes == requested_successes:
            for mission_id in custom_behaviours.allocated_missions[self.robot_id]:
                if not mission_id in ge_behaviours.ge_info['accomplished_missions']:
                    self.all_missions_done = False
                    break
                self.all_missions_done = True
        else:
            if not ge_behaviours.ge_info['move_success']:
                self.add_fitness += 5
            if not ge_behaviours.ge_info['execute_success']:
                self.add_fitness += 10
            if ge_behaviours.ge_info['avoid_success']:
                self.add_fitness -= 5
        return ticks