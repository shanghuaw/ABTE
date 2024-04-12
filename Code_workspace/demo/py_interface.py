import py_trees as pt
import mission_behaviors
from mission_behaviors import get_node_from_string, robot_info
from mission import mission_list

class PyTree(pt.trees.BehaviourTree):
    def __init__(self, bt_string, robot_id=-1, mission_nums=-1):
        str_list = bt_string.split("_")
        self.bt = str_list
        self.robot_id = robot_id
        self.mission_nums = mission_nums
        self.root, has_children = get_node_from_string(self, str_list[0])
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
            newnode, has_children = get_node_from_string(self, str_list[0])
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
        requested_successes = 50
        successes = 0
        while (self.root.status is not pt.common.Status.FAILURE or fails < max_fails) and \
              (self.root.status is not pt.common.Status.SUCCESS or successes < requested_successes) and \
              ticks < max_ticks:
            # sleep(0.05)
            self.root.tick_once()
            ticks += 1
            if self.root.status is pt.common.Status.SUCCESS:
                successes += 1
            else:
                successes = 0
            if self.root.status is pt.common.Status.FAILURE:
                fails += 1
            # for state in env_info['target_state']:
            #     if state == 'Covered':
            #         counts += 1
            success_counts = 0
            failure_counts = 0
            underway_counts = 0
            for m in mission_list[self.mission_nums]:
                if m.state == 'Accomplished' or m.state == 'Timeout':
                    success_counts += 1
                if m.state == 'Idle' and self.robot_id in m.failure_robot:
                    failure_counts += 1
                if m.state == 'Underway':
                    underway_counts += 1
            remain_energy_percent = robot_info['attribute'][self.robot_id][1] / mission_behaviors.INITIAL_ENERGY
            if remain_energy_percent <= 0.1 or success_counts + failure_counts == self.mission_nums:
                print("robot{} stop tick, remain energy percent:{:.2%}, success_counts:{}, failure_counts:{}".format(
                    self.robot_id, remain_energy_percent, success_counts, failure_counts))
                break
            # if not underway_counts == 0:
            #     sleep(1)
        # print("fails:{}, successes:{}".format(fails, successes))
        return ticks