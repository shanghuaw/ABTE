import py_trees as pt
from py_trees import common
from mission import mission_list, mission_states
import threading
from time import sleep

state_lock = threading.Lock()
ENERGY_FACTOR = 5  # 焦耳/米
INITIAL_ENERGY = 20000.0  # 焦耳
RUNNING_SPEED = 100  # 米/秒

robot_info = {
    'current_location': [[50, 50], [50, 50], [50, 50], [50, 50], [50, 50], [50, 50], [50, 50], [50, 50], [50, 50], [50, 50],
                         [50, 50], [50, 50], [50, 50], [50, 50], [50, 50], [50, 50], [50, 50], [50, 50], [50, 50], [50, 50],
                         [50, 50], [50, 50], [50, 50], [50, 50], [50, 50], [50, 50], [50, 50], [50, 50], [50, 50], [50, 50],
                         [50, 50], [50, 50], [50, 50], [50, 50], [50, 50], [50, 50], [50, 50], [50, 50], [50, 50], [50, 50],
                         [50, 50], [50, 50], [50, 50], [50, 50], [50, 50], [50, 50], [50, 50], [50, 50], [50, 50], [50, 50],
                         [50, 50], [50, 50], [50, 50], [50, 50], [50, 50], [50, 50], [50, 50], [50, 50], [50, 50], [50, 50]],
    'mission_index': [-1, -1, -1, -1, -1, -1, -1, -1, -1, -1,
                      -1, -1, -1, -1, -1, -1, -1, -1, -1, -1,
                      -1, -1, -1, -1, -1, -1, -1, -1, -1, -1,
                      -1, -1, -1, -1, -1, -1, -1, -1, -1, -1,
                      -1, -1, -1, -1, -1, -1, -1, -1, -1, -1,
                      -1, -1, -1, -1, -1, -1, -1, -1, -1, -1],
    'attribute': [[0, INITIAL_ENERGY, RUNNING_SPEED], [1, INITIAL_ENERGY, RUNNING_SPEED], [2, INITIAL_ENERGY, RUNNING_SPEED],
                  [3, INITIAL_ENERGY, RUNNING_SPEED], [4, INITIAL_ENERGY, RUNNING_SPEED], [5, INITIAL_ENERGY, RUNNING_SPEED],
                  [6, INITIAL_ENERGY, RUNNING_SPEED], [7, INITIAL_ENERGY, RUNNING_SPEED], [8, INITIAL_ENERGY, RUNNING_SPEED],
                  [9, INITIAL_ENERGY, RUNNING_SPEED], [10, INITIAL_ENERGY, RUNNING_SPEED], [11, INITIAL_ENERGY, RUNNING_SPEED],
                  [12, INITIAL_ENERGY, RUNNING_SPEED], [13, INITIAL_ENERGY, RUNNING_SPEED], [14, INITIAL_ENERGY, RUNNING_SPEED],
                  [15, INITIAL_ENERGY, RUNNING_SPEED], [16, INITIAL_ENERGY, RUNNING_SPEED], [17, INITIAL_ENERGY, RUNNING_SPEED],
                  [18, INITIAL_ENERGY, RUNNING_SPEED], [19, INITIAL_ENERGY, RUNNING_SPEED], [20, INITIAL_ENERGY, RUNNING_SPEED],
                  [21, INITIAL_ENERGY, RUNNING_SPEED], [22, INITIAL_ENERGY, RUNNING_SPEED], [23, INITIAL_ENERGY, RUNNING_SPEED],
                  [24, INITIAL_ENERGY, RUNNING_SPEED], [25, INITIAL_ENERGY, RUNNING_SPEED], [26, INITIAL_ENERGY, RUNNING_SPEED],
                  [27, INITIAL_ENERGY, RUNNING_SPEED], [28, INITIAL_ENERGY, RUNNING_SPEED], [29, INITIAL_ENERGY, RUNNING_SPEED],
                  [30, INITIAL_ENERGY, RUNNING_SPEED], [31, INITIAL_ENERGY, RUNNING_SPEED], [32, INITIAL_ENERGY, RUNNING_SPEED],
                  [33, INITIAL_ENERGY, RUNNING_SPEED], [34, INITIAL_ENERGY, RUNNING_SPEED], [35, INITIAL_ENERGY, RUNNING_SPEED],
                  [36, INITIAL_ENERGY, RUNNING_SPEED], [37, INITIAL_ENERGY, RUNNING_SPEED], [38, INITIAL_ENERGY, RUNNING_SPEED],
                  [39, INITIAL_ENERGY, RUNNING_SPEED], [40, INITIAL_ENERGY, RUNNING_SPEED], [41, INITIAL_ENERGY, RUNNING_SPEED],
                  [42, INITIAL_ENERGY, RUNNING_SPEED], [43, INITIAL_ENERGY, RUNNING_SPEED], [44, INITIAL_ENERGY, RUNNING_SPEED],
                  [45, INITIAL_ENERGY, RUNNING_SPEED], [46, INITIAL_ENERGY, RUNNING_SPEED], [47, INITIAL_ENERGY, RUNNING_SPEED],
                  [48, INITIAL_ENERGY, RUNNING_SPEED], [49, INITIAL_ENERGY, RUNNING_SPEED], [50, INITIAL_ENERGY, RUNNING_SPEED],
                  [51, INITIAL_ENERGY, RUNNING_SPEED], [52, INITIAL_ENERGY, RUNNING_SPEED], [53, INITIAL_ENERGY, RUNNING_SPEED],
                  [54, INITIAL_ENERGY, RUNNING_SPEED], [55, INITIAL_ENERGY, RUNNING_SPEED], [56, INITIAL_ENERGY, RUNNING_SPEED],
                  [57, INITIAL_ENERGY, RUNNING_SPEED], [58, INITIAL_ENERGY, RUNNING_SPEED], [59, INITIAL_ENERGY, RUNNING_SPEED]],
    'ability': [[10, 5, 5, 5], [5, 10, 5, 5], [5, 5, 10, 5], [5, 5, 5, 10],
                [10, 5, 5, 5], [5, 10, 5, 5], [5, 5, 10, 5], [5, 5, 5, 10],
                [10, 5, 5, 5], [5, 10, 5, 5], [5, 5, 10, 5], [5, 5, 5, 10],
                [10, 5, 5, 5], [5, 10, 5, 5], [5, 5, 10, 5], [5, 5, 5, 10],
                [10, 5, 5, 5], [5, 10, 5, 5], [5, 5, 10, 5], [5, 5, 5, 10],
                [10, 5, 5, 5], [5, 10, 5, 5], [5, 5, 10, 5], [5, 5, 5, 10],
                [10, 5, 5, 5], [5, 10, 5, 5], [5, 5, 10, 5], [5, 5, 5, 10],
                [10, 5, 5, 5], [5, 10, 5, 5], [5, 5, 10, 5], [5, 5, 5, 10],
                [10, 5, 5, 5], [5, 10, 5, 5], [5, 5, 10, 5], [5, 5, 5, 10],
                [10, 5, 5, 5], [5, 10, 5, 5], [5, 5, 10, 5], [5, 5, 5, 10],
                [10, 5, 5, 5], [5, 10, 5, 5], [5, 5, 10, 5], [5, 5, 5, 10],
                [10, 5, 5, 5], [5, 10, 5, 5], [5, 5, 10, 5], [5, 5, 5, 10],
                [10, 5, 5, 5], [5, 10, 5, 5], [5, 5, 10, 5], [5, 5, 5, 10],
                [10, 5, 5, 5], [5, 10, 5, 5], [5, 5, 10, 5], [5, 5, 5, 10],
                [10, 5, 5, 5], [5, 10, 5, 5], [5, 5, 10, 5], [5, 5, 5, 10]],
    'is_blocked_by': [-1, -1, -1, -1, -1, -1, -1, -1, -1, -1,
                      -1, -1, -1, -1, -1, -1, -1, -1, -1, -1,
                      -1, -1, -1, -1, -1, -1, -1, -1, -1, -1,
                      -1, -1, -1, -1, -1, -1, -1, -1, -1, -1,
                      -1, -1, -1, -1, -1, -1, -1, -1, -1, -1,
                      -1, -1, -1, -1, -1, -1, -1, -1, -1, -1],  # -1代表没有碰到障碍物，其他值表示障碍物的编号
    'total_path_cost': [0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
                        0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
                        0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
                        0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
                        0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
                        0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    'total_time_cost': [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0,
                        0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0,
                        0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0,
                        0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0,
                        0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0,
                        0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
    'state': ['No Check', 'No Check', 'No Check', 'No Check', 'No Check', 'No Check', 'No Check', 'No Check', 'No Check', 'No Check',
              'No Check', 'No Check', 'No Check', 'No Check', 'No Check', 'No Check', 'No Check', 'No Check', 'No Check', 'No Check',
              'No Check', 'No Check', 'No Check', 'No Check', 'No Check', 'No Check', 'No Check', 'No Check', 'No Check', 'No Check',
              'No Check', 'No Check', 'No Check', 'No Check', 'No Check', 'No Check', 'No Check', 'No Check', 'No Check', 'No Check',
              'No Check', 'No Check', 'No Check', 'No Check', 'No Check', 'No Check', 'No Check', 'No Check', 'No Check', 'No Check',
              'No Check', 'No Check', 'No Check', 'No Check', 'No Check', 'No Check', 'No Check', 'No Check', 'No Check', 'No Check'],
    'accomplished_missions': [list(), list(), list(), list(), list(), list(), list(), list(), list(), list(),
                              list(), list(), list(), list(), list(), list(), list(), list(), list(), list(),
                              list(), list(), list(), list(), list(), list(), list(), list(), list(), list(),
                              list(), list(), list(), list(), list(), list(), list(), list(), list(), list(),
                              list(), list(), list(), list(), list(), list(), list(), list(), list(), list(),
                              list(), list(), list(), list(), list(), list(), list(), list(), list(), list()],
    'prior_missions': [list(), list(), list(), list(), list(), list(), list(), list(), list(), list(),
                       list(), list(), list(), list(), list(), list(), list(), list(), list(), list(),
                       list(), list(), list(), list(), list(), list(), list(), list(), list(), list(),
                       list(), list(), list(), list(), list(), list(), list(), list(), list(), list(),
                       list(), list(), list(), list(), list(), list(), list(), list(), list(), list(),
                       list(), list(), list(), list(), list(), list(), list(), list(), list(), list()],
    'timeout_missions': [list(), list(), list(), list(), list(), list(), list(), list(), list(), list(),
                         list(), list(), list(), list(), list(), list(), list(), list(), list(), list(),
                         list(), list(), list(), list(), list(), list(), list(), list(), list(), list(),
                         list(), list(), list(), list(), list(), list(), list(), list(), list(), list(),
                         list(), list(), list(), list(), list(), list(), list(), list(), list(), list(),
                         list(), list(), list(), list(), list(), list(), list(), list(), list(), list()],
    'score': [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0,
              0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0,
              0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0,
              0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0,
              0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0,
              0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]
}

env_info = {
    'obstacle_range': [[15, 20, 10, 25], [50, 62, 60 ,75], [40, 58, 42, 48]]
}

def get_node_from_string(self, string):
    """
    Returns a py trees behavior or composite given the string
    """
    has_children = False
    if string == 'CheckState':
        node = check_state(self.robot_id)
    elif string == 'GetNeighborMission':
        node = get_neighbor_mission(self.robot_id, self.mission_nums)
    elif string == 'MoveToMission':
        node = move_to_mission(self.robot_id, self.mission_nums)
    elif string == 'IsBlocked?':
        node = is_blocked(self.robot_id)
    elif string == 'AvoidObstacle':
        node = avoid_obstacle(self.robot_id, self.mission_nums)
    elif string == 'ReachTarget?':
        node = reach_target(self.robot_id, self.mission_nums)
    elif string == 'ExecuteMission':
        node = execute_mission(self.robot_id, self.mission_nums)
    elif string == 'Sel':
        node = pt.composites.Selector("Selector", True)
        has_children = True
    elif string == 'Seq':
        node = pt.composites.Sequence("Sequence", True)
        has_children = True
    else:
        raise Exception("Unexpected character", string)

    return node, has_children

def in_range(location, obstacle_range):
    # nums为target_range数组大小
    for i in range(0, len(obstacle_range)):
        if location[0] in range(obstacle_range[i][0], obstacle_range[i][1] + 1)\
                and location[1] in range(obstacle_range[i][2], obstacle_range[i][3] + 1):
            return i
    return -1
class move_to_mission(pt.behaviour.Behaviour):
    def __init__(self, robot_id, mission_nums):
        super(move_to_mission, self).__init__("move to mission")
        self.robot_id = robot_id
        self.mission_nums = mission_nums
        self.move_onestep = {
            'right': [1, 0],
            'left': [-1, 0],
            'up': [0, 1],
            'down': [0, -1]
        }

    def update(self) -> common.Status:
        if not robot_info['state'][self.robot_id] == 'Ready':
            return common.Status.FAILURE
        current_location = robot_info['current_location'][self.robot_id]
        mission_index = robot_info['mission_index'][self.robot_id]
        target_location = mission_list[self.mission_nums][mission_index].location
        path_cost = 0
        while not current_location == target_location:
            # 机器人在移动的过程中遇到了障碍物，则返回失败，进行避障操作
            robot_info['is_blocked_by'][self.robot_id] = in_range(current_location, env_info['obstacle_range'])
            if not robot_info['is_blocked_by'][self.robot_id] == -1:
                energy_cost = ENERGY_FACTOR * path_cost
                robot_info['attribute'][self.robot_id][1] -= energy_cost
                robot_info['total_path_cost'][self.robot_id] += path_cost
                robot_info['total_time_cost'][self.robot_id] += path_cost / robot_info['attribute'][self.robot_id][2]
                robot_info['current_location'][self.robot_id] = current_location
                print("move_to_target, blocked by {}, current location:{}, total path cost:{}, remain energy:{}".
                      format(robot_info['is_blocked_by'][self.robot_id], current_location,
                             robot_info['total_path_cost'][self.robot_id], robot_info['attribute'][self.robot_id][1]))
                sleep(path_cost / robot_info['attribute'][self.robot_id][2] / 50)
                return common.Status.FAILURE
            if target_location[0] > current_location[0]:
                current_location = [i + j for i, j in zip(current_location, self.move_onestep['right'])]
            elif target_location[0] < current_location[0]:
                current_location = [i + j for i, j in zip(current_location, self.move_onestep['left'])]
            elif target_location[1] > current_location[1]:
                current_location = [i + j for i, j in zip(current_location, self.move_onestep['up'])]
            elif target_location[1] < current_location[1]:
                current_location = [i + j for i, j in zip(current_location, self.move_onestep['down'])]
            path_cost += 1
        energy_cost = ENERGY_FACTOR * path_cost
        robot_info['attribute'][self.robot_id][1] -= energy_cost
        robot_info['total_path_cost'][self.robot_id] += path_cost
        robot_info['total_time_cost'][self.robot_id] += path_cost / robot_info['attribute'][self.robot_id][2]
        robot_info['current_location'][self.robot_id] = current_location
        print("robot{} move_to_target, isn't blocked, current location:{}, total path cost:{}, remain energy:{}".
              format(self.robot_id, current_location,
                     robot_info['total_path_cost'][self.robot_id], robot_info['attribute'][self.robot_id][1]))
        sleep(path_cost / robot_info['attribute'][self.robot_id][2] / 50)
        return common.Status.SUCCESS

class avoid_obstacle(pt.behaviour.Behaviour):
    def __init__(self, robot_id, mission_nums):
        super(avoid_obstacle, self).__init__("avoid obstacle")
        self.robot_id = robot_id
        self.mission_nums = mission_nums

    def update(self) -> common.Status:
        if not robot_info['state'][self.robot_id] == 'Ready':
            return common.Status.FAILURE
        current_location = robot_info['current_location'][self.robot_id]
        mission_index = robot_info['mission_index'][self.robot_id]
        target_location = mission_list[self.mission_nums][mission_index].location
        obstacle_id = robot_info['is_blocked_by'][self.robot_id]
        path_cost = 0
        # 场景1：在矩形障碍物的宽边上，但不处于顶点
        if (current_location[0] == env_info['obstacle_range'][obstacle_id][0] or
            current_location[0] == env_info['obstacle_range'][obstacle_id][1]) and \
                not current_location[1] == env_info['obstacle_range'][obstacle_id][2] and \
                not current_location[1] == env_info['obstacle_range'][obstacle_id][3]:
            print("avoid obstacle, situation1")
            # 在x为常量的边， cost1为向下走，cost2为向上走
            cost1 = abs(env_info['obstacle_range'][obstacle_id][2] - current_location[1]) +\
                    abs(current_location[0] - target_location[0]) +\
                    abs(env_info['obstacle_range'][obstacle_id][2] - target_location[1])
            cost2 = abs(env_info['obstacle_range'][obstacle_id][3] - current_location[1]) +\
                    abs(current_location[0] - target_location[0]) +\
                    abs(env_info['obstacle_range'][obstacle_id][3] - target_location[1])
            if cost1 < cost2:
                # 向下走为最优路径
                path_cost += abs(env_info['obstacle_range'][obstacle_id][2] - current_location[1])
                current_location[1] = env_info['obstacle_range'][obstacle_id][2] - 1
            else:
                # 向上走为最优路径
                path_cost += abs(env_info['obstacle_range'][obstacle_id][3] - current_location[1])
                current_location[1] = env_info['obstacle_range'][obstacle_id][3] + 1
            # 如果目标点被障碍物完全挡住，则机器人还需要多绕一条边才算避障成功
            if env_info['obstacle_range'][obstacle_id][2] <= \
                    target_location[1] <= env_info['obstacle_range'][obstacle_id][3]:
                path_cost += abs(env_info['obstacle_range'][obstacle_id][1] - env_info['obstacle_range'][obstacle_id][0])
                if current_location[0] == env_info['obstacle_range'][obstacle_id][0]:
                    current_location[0] = env_info['obstacle_range'][obstacle_id][1] + 1
                else:
                    current_location[0] = env_info['obstacle_range'][obstacle_id][0] - 1
        # 场景2：在矩形障碍物的长边上，但不处于顶点
        elif (current_location[1] == env_info['obstacle_range'][obstacle_id][2] or
              current_location[1] == env_info['obstacle_range'][obstacle_id][3]) and \
                  not current_location[0] == env_info['obstacle_range'][obstacle_id][0] and \
                  not current_location[0] == env_info['obstacle_range'][obstacle_id][1]:
            print("avoid obstacle, situation2")
            # 在y为常量的边，cost1为向左走，cost2为向右走
            cost1 = abs(env_info['obstacle_range'][obstacle_id][0] - current_location[0]) +\
                    abs(current_location[1] - target_location[1]) +\
                    abs(env_info['obstacle_range'][obstacle_id][0] - target_location[0])
            cost2 = abs(env_info['obstacle_range'][obstacle_id][1] - current_location[0]) +\
                    abs(current_location[1] - target_location[1]) +\
                    abs(env_info['obstacle_range'][obstacle_id][1] - target_location[0])
            if cost1 < cost2:
                # 向左走为最优路径
                path_cost += abs(env_info['obstacle_range'][obstacle_id][0] - current_location[0])
                current_location[0] = env_info['obstacle_range'][obstacle_id][0] - 1
            else:
                # 向右走为最优路径
                path_cost += abs(env_info['obstacle_range'][obstacle_id][1] - current_location[0])
                current_location[0] = env_info['obstacle_range'][obstacle_id][1] + 1
            # 如果目标点被障碍物完全挡住，则机器人还需要多绕一条边才算避障成功
            if env_info['obstacle_range'][obstacle_id][0] <= \
                    target_location[0] <= env_info['obstacle_range'][obstacle_id][1]:
                path_cost += abs(env_info['obstacle_range'][obstacle_id][3] - env_info['obstacle_range'][obstacle_id][2])
                if current_location[1] == env_info['obstacle_range'][obstacle_id][2]:
                    current_location[1] = env_info['obstacle_range'][obstacle_id][3] + 1
                else:
                    current_location[1] = env_info['obstacle_range'][obstacle_id][2] - 1
        # 场景3：正好位于矩形障碍物的顶点上
        else:
            print("avoid obstacle, situation3")
            path_cost += (abs(current_location[0] - target_location[0]) + abs(current_location[1] - target_location[1]))
            current_location = target_location
        robot_info['current_location'][self.robot_id] = current_location
        robot_info['is_blocked_by'][self.robot_id] = -1
        energy_cost = ENERGY_FACTOR * path_cost
        robot_info['attribute'][self.robot_id][1] -= energy_cost
        robot_info['total_path_cost'][self.robot_id] += path_cost
        robot_info['total_time_cost'][self.robot_id] += path_cost / robot_info['attribute'][self.robot_id][2]
        print("after avoid_obstacle, current_location:{}, total path cost:{}, remain energy:{}".format(
            current_location, robot_info['total_path_cost'][self.robot_id], robot_info['attribute'][self.robot_id][1]))
        sleep(path_cost / robot_info['attribute'][self.robot_id][2] / 50)
        return common.Status.SUCCESS

class check_state(pt.behaviour.Behaviour):
    def __init__(self, robot_id):
        super(check_state, self).__init__("check state")
        self.robot_id = robot_id
        robot_info['state'][self.robot_id] = 'No Check'

    def update(self) -> common.Status:
        robot_info['state'][self.robot_id] = 'Ready'
        if robot_info['attribute'][self.robot_id][1] / INITIAL_ENERGY <= 0.1:
            print("robot{} remain energy percent is less than 10%, check state failure")
            return common.Status.FAILURE
        return common.Status.SUCCESS
    
class get_neighbor_mission(pt.behaviour.Behaviour):
    def __init__(self, robot_id, mission_nums):
        super(get_neighbor_mission, self).__init__("get neighbor mission")
        self.robot_id = robot_id
        self.mission_nums = mission_nums

    def update(self) -> common.Status:
        current_location = robot_info['current_location'][self.robot_id]
        min_distance = 200
        mission_index = robot_info['mission_index'][self.robot_id]
        # 该机器人有正在执行的任务（即行为树上一次tick执行了避障），则不用搜索临近任务
        if not mission_index == -1 and mission_list[self.mission_nums][mission_index].state == mission_states[1]:
            print("robot{} current location:{}, mission{} Underway".format(
                self.robot_id, current_location, mission_index))
            return common.Status.SUCCESS
        mission_size = len(mission_list[self.mission_nums])
        for i in range(0, mission_size):
            # 检查任务是否已经被执行或已被其他机器人捕获
            if mission_list[self.mission_nums][i].state == mission_states[0] and self.robot_id not in mission_list[self.mission_nums][i].failure_robot:
                distance = abs(mission_list[self.mission_nums][i].location[0] - current_location[0]) +\
                           abs(mission_list[self.mission_nums][i].location[1] - current_location[1])
                if distance < min_distance:
                    mission_index = i
                min_distance = min(min_distance, distance)
        # 未获取到最近的目标
        if mission_index == -1:
            return common.Status.FAILURE
        state_lock.acquire()
        mission_list[self.mission_nums][mission_index].state = mission_states[1]  # 将最近的目标点状态置为Underway
        robot_info['mission_index'][self.robot_id] = mission_index
        state_lock.release()
        print("robot{} current location:{}, get neighbor mission:{}".format(self.robot_id, current_location, mission_index))
        return common.Status.SUCCESS

class is_blocked(pt.behaviour.Behaviour):
    def __init__(self, robot_id):
        super(is_blocked, self).__init__("is blocked")
        self.robot_id = robot_id

    def update(self) -> common.Status:
        if robot_info['is_blocked_by'][self.robot_id] == -1:
            return common.Status.FAILURE
        else:
            return common.Status.SUCCESS

class reach_target(pt.behaviour.Behaviour):
    def __init__(self, robot_id, mission_nums):
        super(reach_target, self).__init__("reach target")
        self.robot_id = robot_id
        self.mission_nums = mission_nums

    def update(self) -> common.Status:
        current_location = robot_info['current_location'][self.robot_id]
        mission_index = robot_info['mission_index'][self.robot_id]
        target_location = mission_list[self.mission_nums][mission_index].location
        if current_location == target_location:
            print("robot{} reach mission{}, ready for executing".format(self.robot_id, mission_index))
            return common.Status.SUCCESS
        else:
            return common.Status.FAILURE

class execute_mission(pt.behaviour.Behaviour):
    def __init__(self, robot_id, mission_nums):
        super(execute_mission, self).__init__("execute mission")
        self.robot_id = robot_id
        self.mission_nums = mission_nums

    def update(self) -> common.Status:
        mission_index = robot_info['mission_index'][self.robot_id]
        mission = mission_list[self.mission_nums][mission_index]
        ability_value = robot_info['ability'][self.robot_id][mission.type]
        # time_cost = (3 - ability_value / 5) * mission.b
        time_cost = mission.b / ability_value
        energy_cost = time_cost * mission.a
        # 如果执行任务之后剩余能量小于5%，则不执行当前任务
        if (robot_info['attribute'][self.robot_id][1] - energy_cost) / INITIAL_ENERGY < 0.05:
            state_lock.acquire()
            mission_list[self.mission_nums][mission_index].state = mission_states[0]
            mission_list[self.mission_nums][mission_index].failure_robot.add(self.robot_id)
            robot_info['mission_index'][self.robot_id] = -1
            state_lock.release()
            print("robot{} remain energy will be {} after executing mission{}, failure".format(
                self.robot_id, robot_info['attribute'][self.robot_id][1] - energy_cost, mission_index))
            return common.Status.FAILURE
        robot_info['attribute'][self.robot_id][1] -= energy_cost
        robot_info['total_time_cost'][self.robot_id] += time_cost
        sleep(time_cost / 100)
        # 计算当前任务得分
        if not mission.time_limit == 0:
            # 时间窗口剩余时间越少，得分越低，执行任务时间超过了时间窗口，则不得分
            if mission.time_limit - robot_info['total_time_cost'][self.robot_id] >= 0:
                score = mission.priority * (3 - mission.type)
                mission_list[self.mission_nums][mission_index].state = mission_states[2]
                robot_info['accomplished_missions'][self.robot_id].append(mission_index)
                robot_info['prior_missions'][self.robot_id].append(mission_index)
            else:
                score = 0
                mission_list[self.mission_nums][mission_index].state = mission_states[3]
                robot_info['timeout_missions'][self.robot_id].append(mission_index)
        else:
            score = mission.priority
            mission_list[self.mission_nums][mission_index].state = mission_states[2]
            robot_info['accomplished_missions'][self.robot_id].append(mission_index)
        print("robot{} mission{} score:{}".format(self.robot_id, mission_index, score))
        robot_info['score'][self.robot_id] += score
        robot_info['mission_index'][self.robot_id] = -1
        print("robot{} mission{} accomplished".format(self.robot_id, mission_index))
        return common.Status.SUCCESS