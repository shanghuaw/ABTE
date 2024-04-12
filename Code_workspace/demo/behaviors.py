import py_trees as pt
from py_trees import common, blackboard
import random
from time import sleep
import threading
from mission import mission_list

state_lock = threading.Lock()
test_info = {
    'init_position': [1, 2],
    'cube0_position': [8, 15],
    'cube1_position': [10, 16],
    'cube2_position': [13, 9],
    'place_position': [17, 6],
    'current_position': 'init_position',
    'hold_state': [False, False, False],
    'placed_state': [False, False, False],
    'path_cost': 0,
    'complete': False
}

robot_info = {
    'current_location': [[0, 0], [0, 0], [0, 0]],
    'mission_index': [-1, -1, -1],
    'attribute': [[0, 10000, 4], [1, 10000, 4], [2, 10000, 4]],
    'ability': [[10, 2, 6], [8, 10, 3], [9, 4, 10]],
    'is_blocked_by': [-1, -1, -1],  # -1代表没有碰到障碍物，其他值表示障碍物的编号
    'total_path_cost': [0, 0, 0],
    'total_time_cost': [0.0, 0.0, 0.0],
    'state': ['No Check', 'No Check', 'No Check'],
    'covered_targets': [0, 0, 0],
    'energy_factor': 16
}

env_info = {
    # 第一个表示[6, 20], [6, 23], [13, 20], [13, 23]四个点围成的矩形
    'obstacle_range': [[6, 13, 20, 23], [26, 31, 30 ,38], [38, 42, 10, 15]],
    # 'target_locations': [[47, 13], [45, 14], [43, 7], [24, 32], [23, 4], [48, 33], [34, 41], [33, 45], [29, 44], [27, 50],
    #                    [38, 8], [21, 42], [10, 29], [37, 27], [14, 20], [11, 29], [13, 3], [34, 15], [48, 47], [23, 23],
    #                    [47, 15], [7, 28], [20, 24], [0, 16], [15, 28], [3, 31], [48, 34], [32, 39], [13, 18], [3, 42],
    #                    [22, 28], [2, 39], [37, 22], [20, 40], [23, 7], [3, 9], [41, 41], [45, 10], [13, 9], [8, 26],
    #                    [21, 25], [35, 20], [44, 13], [12, 48], [35, 48], [19, 35], [18, 22], [33, 1], [19, 22], [49, 7],
    #                    [16, 29], [39, 32], [11, 39], [40, 33], [0, 6], [10, 31], [31, 26], [10, 28], [8, 37], [34, 49],
    #                    [21, 28], [38, 18], [36, 1], [7, 40], [45, 3], [42, 0], [17, 46], [20, 37], [8, 8], [21, 11],
    #                    [4, 47], [49, 26], [38, 32], [50, 9], [1, 43], [34, 2], [13, 26], [27, 0], [5, 18], [2, 13],
    #                    [15, 18], [1, 8], [45, 29], [23, 5], [21, 18], [34, 40], [29, 45], [14, 40], [27, 15], [13, 8],
    #                    [43, 13], [1, 46], [43, 43], [9, 48], [12, 24], [13, 7], [35, 1], [4, 49], [4, 3], [33, 25]],
    # # 每个目标点有Idle，Underway，Covered三种状态
    # 'target_state': ['Idle', 'Idle', 'Idle', 'Idle', 'Idle', 'Idle', 'Idle', 'Idle', 'Idle', 'Idle',
    #                  'Idle', 'Idle', 'Idle', 'Idle', 'Idle', 'Idle', 'Idle', 'Idle', 'Idle', 'Idle',
    #                  'Idle', 'Idle', 'Idle', 'Idle', 'Idle', 'Idle', 'Idle', 'Idle', 'Idle', 'Idle',
    #                  'Idle', 'Idle', 'Idle', 'Idle', 'Idle', 'Idle', 'Idle', 'Idle', 'Idle', 'Idle',
    #                  'Idle', 'Idle', 'Idle', 'Idle', 'Idle', 'Idle', 'Idle', 'Idle', 'Idle', 'Idle',
    #                  'Idle', 'Idle', 'Idle', 'Idle', 'Idle', 'Idle', 'Idle', 'Idle', 'Idle', 'Idle',
    #                  'Idle', 'Idle', 'Idle', 'Idle', 'Idle', 'Idle', 'Idle', 'Idle', 'Idle', 'Idle',
    #                  'Idle', 'Idle', 'Idle', 'Idle', 'Idle', 'Idle', 'Idle', 'Idle', 'Idle', 'Idle',
    #                  'Idle', 'Idle', 'Idle', 'Idle', 'Idle', 'Idle', 'Idle', 'Idle', 'Idle', 'Idle',
    #                  'Idle', 'Idle', 'Idle', 'Idle', 'Idle', 'Idle', 'Idle', 'Idle', 'Idle', 'Idle']
    # 'target_locations': [[9, 19], [11, 25], [25, 31], [33, 34]],
    # 'target_state': [False, False, False, False]
}

def get_node_from_string(self, string):
    """
    Returns a py trees behavior or composite given the string
    """
    has_children = False
    if string == "MoveToCube0":
        node = move_to_position('cube0_position')
    elif string == "MoveToCube1":
        node = move_to_position('cube1_position')
    elif string == "MoveToCube2":
        node = move_to_position('cube2_position')
    elif string == "MoveToPlace":
        node = move_to_position('place_position')
    elif string == "PickObject":
        node = pick_up()
    elif string == "PlaceObject":
        node = put_down()
    elif string == "PlacedCube0?":
        node = check_place_state('cube0')
    elif string == "PlacedCube1?":
        node = check_place_state('cube1')
    elif string == "PlacedCube2?":
        node = check_place_state('cube2')
    elif string == "HoldCube?":
        node = check_hold_state()
    elif string == "TaskDone?":
        node = task_done()
    elif string == 'TestBlackboard':
        node = test_blackborad()
    elif string == 'TestBlackboardRead':
        node = test_blackborad_read()
    elif string == 'CheckState':
        node = check_state(self.robot_id)
    elif string == 'GetNeighborTarget':
        node = get_neighbor_target(self.robot_id)
    elif string == 'MoveToTarget':
        node = move_to_target(self.robot_id)
    elif string == 'IsBlocked?':
        node = is_blocked(self.robot_id)
    elif string == 'AvoidObstacle':
        node = avoid_obstacle(self.robot_id)
    elif string == 'ReachTarget?':
        node = reach_target(self.robot_id)
    elif string == 'Sel':
        node = pt.composites.Selector("Selector", True)
        has_children = True
    elif string == 'Seq':
        node = pt.composites.Sequence("Sequence", True)
        has_children = True
    else:
        raise Exception("Unexpected character", string)

    return node, has_children

class move_to_position(pt.behaviour.Behaviour):
    def __init__(self, position):
        super(move_to_position, self).__init__('move to {}'.format(position))
        self.current_position = test_info['current_position']
        self.target_position = position

    def update(self) -> common.Status:
        test_info['path_cost'] += abs(test_info[self.target_position][0] - test_info[self.current_position][0]) +\
                         abs(test_info[self.target_position][1] - test_info[self.current_position][1])
        test_info['current_position'] = self.target_position
        return common.Status.SUCCESS

class pick_up(pt.behaviour.Behaviour):
    def __init__(self):
        super(pick_up, self).__init__(name = 'pick up')

    def update(self) -> common.Status:
        for state in test_info['hold_state']:
            if state:
                return common.Status.FAILURE
        else:
            if test_info['current_position'] == 'cube0_position' and not test_info['placed_state'][0]:
                test_info['hold_state'][0] = True
                return common.Status.SUCCESS
            elif test_info['current_position'] == 'cube1_position' and not test_info['placed_state'][1]:
                test_info['hold_state'][1] = True
                return common.Status.SUCCESS
            elif test_info['current_position'] == 'cube2_position' and not test_info['placed_state'][2]:
                test_info['hold_state'][2] = True
                return common.Status.SUCCESS
            else:
                return common.Status.FAILURE

class put_down(pt.behaviour.Behaviour):
    def __init__(self):
        super(put_down, self).__init__('put down')

    def update(self) -> common.Status:
        if test_info['current_position'] == 'place_position':
            if test_info['hold_state'][0]:
                test_info['placed_state'][0] = True
                test_info['hold_state'][0] = False
                return common.Status.SUCCESS
            elif test_info['hold_state'][1]:
                test_info['placed_state'][1] = True
                test_info['hold_state'][1] = False
                return common.Status.SUCCESS
            elif test_info['hold_state'][2]:
                test_info['placed_state'][2] = True
                test_info['hold_state'][2] = False
                return common.Status.SUCCESS
            else:
                return common.Status.FAILURE
        else:
            return common.Status.FAILURE

class check_hold_state(pt.behaviour.Behaviour):
    def __init__(self):
        super(check_hold_state, self).__init__('check hold state')

    def update(self) -> common.Status:
        for state in test_info['hold_state']:
            if state:
                return common.Status.SUCCESS
        return common.Status.FAILURE

class check_place_state(pt.behaviour.Behaviour):
    def __init__(self, object_name):
        super(check_place_state, self).__init__('check {} place state'.format(object_name))
        self.object_name = object_name

    def update(self) -> common.Status:
        if self.object_name == 'cube0' and test_info['placed_state'][0]:
            return common.Status.SUCCESS
        if self.object_name == 'cube1' and test_info['placed_state'][1]:
            return common.Status.SUCCESS
        if self.object_name == 'cube2' and test_info['placed_state'][2]:
            return common.Status.SUCCESS
        return common.Status.FAILURE

class task_done(pt.behaviour.Behaviour):
    def __init__(self):
        super(task_done, self).__init__("task done?")

    def update(self):
        for state in test_info['placed_state']:
            if not state:
                return pt.common.Status.FAILURE
        test_info['complete'] = True
        return pt.common.Status.SUCCESS

class test_blackborad(pt.behaviour.Behaviour):
    def __init__(self):
        super(test_blackborad, self).__init__("test blackborad")
        self.optional_states = ['Ready', 'Energy Deficiency', 'Component Damage', 'Offline']
        self.blackboard = blackboard.Client(name = 'Write')
        self.blackboard.register_key(key='robot_state', access=common.Access.WRITE)
        self.blackboard.robot_state = str
        self.state = None

    def update(self):
        if self.state is None:
            self.state = pt.common.Status.RUNNING
        elif self.state is pt.common.Status.RUNNING:
            sleep(5)
            index = random.randint(0, 3)
            self.blackboard.robot_state = self.optional_states[index]
            self.state = pt.common.Status.SUCCESS
        return self.state

class test_blackborad_read(pt.behaviour.Behaviour):
    def __init__(self):
        super(test_blackborad_read, self).__init__("test blackborad read")
        self.blackboard = blackboard.Client(name='Read')
        self.blackboard.register_key(key='robot_state', access=common.Access.READ)

    def update(self):
        print(self.blackboard.robot_state)
        return pt.common.Status.SUCCESS

def in_range(location, obstacle_range):
    # nums为target_range数组大小
    for i in range(0, len(obstacle_range)):
        if location[0] in range(obstacle_range[i][0], obstacle_range[i][1] + 1)\
                and location[1] in range(obstacle_range[i][2], obstacle_range[i][3] + 1):
            return i
    return -1

class move_to_target(pt.behaviour.Behaviour):
    def __init__(self, robot_id):
        super(move_to_target, self).__init__("move to target")
        self.robot_id = robot_id
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
        target_location = env_info['target_locations'][robot_info['mission_index'][self.robot_id]]
        path_cost =0
        while not current_location == target_location:
            # 机器人在移动的过程中遇到了障碍物，则返回失败，进行避障操作
            robot_info['is_blocked_by'][self.robot_id] = in_range(current_location, env_info['obstacle_range'])
            if not robot_info['is_blocked_by'][self.robot_id] == -1:
                energy_cost = robot_info['energy_factor'] * path_cost
                robot_info['attribute'][self.robot_id][1] -= energy_cost
                robot_info['current_location'][self.robot_id] = current_location
                print("move_to_target, blocked by {}, current location:{}, total path cost:{}, remain energy:{}".
                      format(robot_info['is_blocked_by'][self.robot_id], current_location,
                             robot_info['total_path_cost'][self.robot_id], robot_info['attribute'][self.robot_id][1]))
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
        energy_cost = robot_info['energy_factor'] * path_cost
        robot_info['attribute'][self.robot_id][1] -= energy_cost
        robot_info['total_path_cost'][self.robot_id] += path_cost
        robot_info['current_location'][self.robot_id] = current_location
        print("robot{} move_to_target, isn't blocked, current location:{}, total path cost:{}, remain energy:{}".
              format(self.robot_id, current_location,
                     robot_info['total_path_cost'][self.robot_id], robot_info['attribute'][self.robot_id][1]))
        return common.Status.SUCCESS

class avoid_obstacle(pt.behaviour.Behaviour):
    def __init__(self, robot_id):
        super(avoid_obstacle, self).__init__("avoid obstacle")
        self.robot_id = robot_id

    def update(self) -> common.Status:
        if not robot_info['state'][self.robot_id] == 'Ready':
            return common.Status.FAILURE
        current_location = robot_info['current_location'][self.robot_id]
        target_location = env_info['target_locations'][robot_info['mission_index'][self.robot_id]]
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
        energy_cost = robot_info['energy_factor'] * path_cost
        robot_info['attribute'][self.robot_id][1] -= energy_cost
        robot_info['total_path_cost'][self.robot_id] += path_cost
        print("after avoid_obstacle, current_location:{}, total path cost:{}, remain energy:{}".format(
            current_location, robot_info['total_path_cost'][self.robot_id], robot_info['attribute'][self.robot_id][1]))
        return common.Status.SUCCESS

class check_state(pt.behaviour.Behaviour):
    def __init__(self, robot_id):
        super(check_state, self).__init__("check state")
        self.robot_id = robot_id
        robot_info['state'][self.robot_id] = 'No Check'

    def update(self) -> common.Status:
        robot_info['state'][self.robot_id] = 'Ready'
        if robot_info['attribute'][self.robot_id][1] / 10000 <= 0.1:
            print("robot{} remain energy percent is less than 10%, check state failure")
            return common.Status.FAILURE
        return common.Status.SUCCESS

class get_neighbor_target(pt.behaviour.Behaviour):
    def __init__(self, robot_id):
        super(get_neighbor_target, self).__init__("get neighbor target")
        self.robot_id = robot_id

    def update(self) -> common.Status:
        current_location = robot_info['current_location'][self.robot_id]
        target_size = len(env_info['target_locations'])
        min_distance = 200
        mission_index = robot_info['mission_index'][self.robot_id]
        if not mission_index == -1 and env_info['target_state'][mission_index] == 'Underway':
            print("robot{} current location:{}, target:{} Underway".format(
                self.robot_id, current_location, env_info['target_locations'][mission_index]))
            return common.Status.SUCCESS
        for i in range(0, target_size):
            # 检查目标是否已经被覆盖或已被其他机器人捕获
            if env_info['target_state'][i] == 'Idle':
                distance = abs(env_info['target_locations'][i][0] - current_location[0]) +\
                           abs(env_info['target_locations'][i][1] - current_location[1])
                if distance < min_distance:
                    mission_index = i
                min_distance = min(min_distance, distance)
        # 未获取到最近的目标
        if mission_index == -1:
            return common.Status.FAILURE
        state_lock.acquire()
        env_info['target_state'][mission_index] = 'Underway'  # 将最近的目标点状态置为'Underway'
        robot_info['mission_index'][self.robot_id] = mission_index
        state_lock.release()
        print("robot{} current location:{}, get neighbor target:{}".format(
            self.robot_id, current_location, env_info['target_locations'][mission_index]))
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
    def __init__(self, robot_id):
        super(reach_target, self).__init__("reach target")
        self.robot_id = robot_id

    def update(self) -> common.Status:
        current_location = robot_info['current_location'][self.robot_id]
        target_location = env_info['target_locations'][robot_info['mission_index'][self.robot_id]]
        if current_location == target_location:
            state_lock.acquire()
            env_info['target_state'][robot_info['mission_index'][self.robot_id]] = 'Covered'
            robot_info['mission_index'][self.robot_id] = -1
            robot_info['covered_targets'][self.robot_id] += 1
            state_lock.release()
            return common.Status.SUCCESS
        else:
            return common.Status.FAILURE