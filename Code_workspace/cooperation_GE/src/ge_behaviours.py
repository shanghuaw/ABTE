import py_trees as pt
from mission import mission_list, mission_states
import custom_behaviours

ENERGY_FACTOR = 40  # 焦耳/米
INITIAL_ENERGY = 5000000.0  # 焦耳
RUNNING_SPEED = 8  # 米/秒

ge_info = {
    'is_blocked_by': -1,
    'blocked': False,
    'mission_todo': -1,
    'reached': False,
    'robot_state': 'No Check',
    'move_success': False,
    'execute_success': False,
    'avoid_success': False,
    'current_location': [0, 0],
    'current_energy': INITIAL_ENERGY,
    'total_path_cost': 0,
    'total_time_cost': 0.0,
    'total_score': 0.0,
    'accomplished_missions': list(),
    'mission_counts': 0,
    'is_mission': [False, False, False]
}

def get_node_from_string(self, string):
    """
    Returns a py trees behavior or composite given the string
    """
    has_children = False
    if string == "CheckState":
        node = check_state(self.robot_id)
    elif string == "GetMission":
        node = get_mission(self.robot_id)
    elif string == "MoveToMission":
        node = move_to_mission(self.robot_id)
    elif string == "Rescue?":
        node = rescue(self.robot_id)
    elif string == "OutFire?":
        node = outfire(self.robot_id)
    elif string == "Carry?":
        node = carry(self.robot_id)
    elif string == "IsBlocked?":
        node = is_blocked(self.robot_id)
    elif string == "AvoidObstacle":
        node = avoid_obstacle(self.robot_id)
    elif string == "ReachMission?":
        node = reach_mission(self.robot_id)
    elif string == "ExecuteRescue":
        node = execute_mission(self.robot_id, 0)
    elif string == "ExecuteOutFire":
        node = execute_mission(self.robot_id, 1)
    elif string == "ExecuteCarry":
        node = execute_mission(self.robot_id, 2)
    elif string == 'Sel':
        node = pt.composites.Selector("Selector", True)
        has_children = True
    elif string == 'Seq':
        node = pt.composites.Sequence("Sequence", True)
        has_children = True
    else:
        raise Exception("Unexpected character", string)

    return node, has_children

def in_range(location, ranges):
    for i in range(0, len(ranges)):
        if location[0] in range(ranges[i][0], ranges[i][1] + 1)\
                and location[1] in range(ranges[i][2], ranges[i][3] + 1):
            return i
    return -1

class move_to_mission(pt.behaviour.Behaviour):
    def __init__(self, robot_id):
        super(move_to_mission, self).__init__("move to mission")
        self.robot_id = robot_id
        self.move_onestep = {
            'right': [1, 0],
            'left': [-1, 0],
            'up': [0, 1],
            'down': [0, -1]
        }

    def update(self) -> pt.common.Status:
        if not ge_info['robot_state'] == 'Ready' or ge_info['mission_todo'] == -1:
            return pt.common.Status.FAILURE
        current_location = ge_info['current_location']
        mission_id = ge_info['mission_todo']
        target_location = mission_list[mission_id].location
        path_cost = 0
        while not current_location == target_location:
            # 机器人在移动的过程中遇到了障碍物，则返回失败，进行避障操作
            ge_info['is_blocked_by'] = in_range(current_location, custom_behaviours.obstacle_range)
            if not ge_info['is_blocked_by'] == -1:
                energy_cost = ENERGY_FACTOR * path_cost
                ge_info['current_energy'] -= energy_cost
                ge_info['total_path_cost'] += path_cost
                ge_info['total_time_cost'] += path_cost / RUNNING_SPEED
                ge_info['current_location'] = current_location
                # print("robot{} is blocked by {}".format(self.robot_id, ge_info['is_blocked_by']))
                return pt.common.Status.FAILURE
            if target_location[0] > current_location[0]:
                current_location = [i + j for i, j in zip(current_location, self.move_onestep['right'])]
            elif target_location[0] < current_location[0]:
                current_location = [i + j for i, j in zip(current_location, self.move_onestep['left'])]
            elif target_location[1] > current_location[1]:
                current_location = [i + j for i, j in zip(current_location, self.move_onestep['up'])]
            elif target_location[1] < current_location[1]:
                current_location = [i + j for i, j in zip(current_location, self.move_onestep['down'])]
            path_cost += 4
        energy_cost = ENERGY_FACTOR * path_cost
        ge_info['current_energy'] -= energy_cost
        ge_info['total_path_cost'] += path_cost
        ge_info['total_time_cost'] += path_cost / RUNNING_SPEED
        ge_info['current_location'] = current_location
        ge_info['move_success'] = True
        return pt.common.Status.SUCCESS

class avoid_obstacle(pt.behaviour.Behaviour):
    def __init__(self, robot_id):
        super(avoid_obstacle, self).__init__("avoid obstacle")
        self.robot_id = robot_id

    def update(self) -> pt.common.Status:
        if not ge_info['robot_state'] == 'Ready' or ge_info['mission_todo'] == -1 or not ge_info['blocked']:
            return pt.common.Status.FAILURE
        current_location = ge_info['current_location']
        mission_id = ge_info['mission_todo']
        target_location = mission_list[mission_id].location
        obstacle_id = ge_info['is_blocked_by']
        path_cost = 0
        # 场景1：在矩形障碍物的宽边上，但不处于顶点
        if (current_location[0] == custom_behaviours.obstacle_range[obstacle_id][0] or
            current_location[0] == custom_behaviours.obstacle_range[obstacle_id][1]) and \
                not current_location[1] == custom_behaviours.obstacle_range[obstacle_id][2] and \
                not current_location[1] == custom_behaviours.obstacle_range[obstacle_id][3]:
            # 在x为常量的边， cost1为向下走，cost2为向上走
            cost1 = abs(custom_behaviours.obstacle_range[obstacle_id][2] - current_location[1]) +\
                    abs(current_location[0] - target_location[0]) +\
                    abs(custom_behaviours.obstacle_range[obstacle_id][2] - target_location[1])
            cost2 = abs(custom_behaviours.obstacle_range[obstacle_id][3] - current_location[1]) +\
                    abs(current_location[0] - target_location[0]) +\
                    abs(custom_behaviours.obstacle_range[obstacle_id][3] - target_location[1])
            if cost1 < cost2:
                # 向下走为最优路径
                path_cost += abs(custom_behaviours.obstacle_range[obstacle_id][2] - current_location[1]) * 4
                current_location[1] = custom_behaviours.obstacle_range[obstacle_id][2] - 1
            else:
                # 向上走为最优路径
                path_cost += abs(custom_behaviours.obstacle_range[obstacle_id][3] - current_location[1]) * 4
                current_location[1] = custom_behaviours.obstacle_range[obstacle_id][3] + 1
            # 如果目标点被障碍物完全挡住，则机器人还需要多绕一条边才算避障成功
            if custom_behaviours.obstacle_range[obstacle_id][2] <= \
                    target_location[1] <= custom_behaviours.obstacle_range[obstacle_id][3]:
                path_cost += abs(custom_behaviours.obstacle_range[obstacle_id][1] -
                                 custom_behaviours.obstacle_range[obstacle_id][0]) * 4
                if current_location[0] == custom_behaviours.obstacle_range[obstacle_id][0]:
                    current_location[0] = custom_behaviours.obstacle_range[obstacle_id][1] + 1
                else:
                    current_location[0] = custom_behaviours.obstacle_range[obstacle_id][0] - 1
        # 场景2：在矩形障碍物的长边上，但不处于顶点
        elif (current_location[1] == custom_behaviours.obstacle_range[obstacle_id][2] or
              current_location[1] == custom_behaviours.obstacle_range[obstacle_id][3]) and \
                  not current_location[0] == custom_behaviours.obstacle_range[obstacle_id][0] and \
                  not current_location[0] == custom_behaviours.obstacle_range[obstacle_id][1]:
            # 在y为常量的边，cost1为向左走，cost2为向右走
            cost1 = abs(custom_behaviours.obstacle_range[obstacle_id][0] - current_location[0]) +\
                    abs(current_location[1] - target_location[1]) +\
                    abs(custom_behaviours.obstacle_range[obstacle_id][0] - target_location[0])
            cost2 = abs(custom_behaviours.obstacle_range[obstacle_id][1] - current_location[0]) +\
                    abs(current_location[1] - target_location[1]) +\
                    abs(custom_behaviours.obstacle_range[obstacle_id][1] - target_location[0])
            if cost1 < cost2:
                # 向左走为最优路径
                path_cost += abs(custom_behaviours.obstacle_range[obstacle_id][0] - current_location[0]) * 4
                current_location[0] = custom_behaviours.obstacle_range[obstacle_id][0] - 1
            else:
                # 向右走为最优路径
                path_cost += abs(custom_behaviours.obstacle_range[obstacle_id][1] - current_location[0]) * 4
                current_location[0] = custom_behaviours.obstacle_range[obstacle_id][1] + 1
            # 如果目标点被障碍物完全挡住，则机器人还需要多绕一条边才算避障成功
            if custom_behaviours.obstacle_range[obstacle_id][0] <= \
                    target_location[0] <= custom_behaviours.obstacle_range[obstacle_id][1]:
                path_cost += abs(custom_behaviours.obstacle_range[obstacle_id][3] -
                                 custom_behaviours.obstacle_range[obstacle_id][2]) * 4
                if current_location[1] == custom_behaviours.obstacle_range[obstacle_id][2]:
                    current_location[1] = custom_behaviours.obstacle_range[obstacle_id][3] + 1
                else:
                    current_location[1] = custom_behaviours.obstacle_range[obstacle_id][2] - 1
        # 场景3：正好位于矩形障碍物的顶点上
        else:
            path_cost += (abs(current_location[0] - target_location[0]) + abs(current_location[1] - target_location[1])) * 4
            current_location = target_location
        ge_info['current_location'] = current_location
        ge_info['is_blocked_by'] = -1
        ge_info['blocked'] = False
        energy_cost = ENERGY_FACTOR * path_cost
        ge_info['current_energy'] -= energy_cost
        ge_info['total_path_cost'] += path_cost
        ge_info['total_time_cost'] += path_cost / RUNNING_SPEED
        ge_info['avoid_success'] = True
        return pt.common.Status.SUCCESS

class check_state(pt.behaviour.Behaviour):
    def __init__(self, robot_id):
        super(check_state, self).__init__("check state")
        self.robot_id = robot_id
        ge_info['robot_state'] = 'No Check'

    def update(self) -> pt.common.Status:
        ge_info['robot_state'] = 'Ready'
        if ge_info['current_energy'] / INITIAL_ENERGY < 0.05:
            return pt.common.Status.FAILURE
        return pt.common.Status.SUCCESS

class get_mission(pt.behaviour.Behaviour):
    def __init__(self, robot_id):
        super(get_mission, self).__init__("get mission")
        self.robot_id = robot_id

    def update(self) -> pt.common.Status:
        # 阻塞状态下不执行该动作
        if not ge_info['is_blocked_by'] == -1:
            return pt.common.Status.SUCCESS
        if not ge_info['robot_state'] == 'Ready':
            return pt.common.Status.FAILURE
        mission_num = len(ge_info['accomplished_missions'])
        if mission_num < len(custom_behaviours.allocated_missions[self.robot_id]):
            ge_info['mission_todo'] = custom_behaviours.allocated_missions[self.robot_id][mission_num]
            return pt.common.Status.SUCCESS
        else:
            return pt.common.Status.FAILURE

class rescue(pt.behaviour.Behaviour):
    def __init__(self, robot_id):
        super(rescue, self).__init__("rescue?")
        self.robot_id = robot_id

    def update(self) -> pt.common.Status:
        if not ge_info['reached']:
            return pt.common.Status.FAILURE
        mission_id = ge_info['mission_todo']
        mission_type = mission_list[mission_id].type
        if mission_type == 0:
            ge_info['is_mission'][0] = True
            return pt.common.Status.SUCCESS
        return pt.common.Status.FAILURE

class outfire(pt.behaviour.Behaviour):
    def __init__(self, robot_id):
        super(outfire, self).__init__("outfire?")
        self.robot_id = robot_id

    def update(self) -> pt.common.Status:
        if not ge_info['reached']:
            return pt.common.Status.FAILURE
        mission_id = ge_info['mission_todo']
        mission_type = mission_list[mission_id].type
        if mission_type == 1:
            ge_info['is_mission'][1] = True
            return pt.common.Status.SUCCESS
        return pt.common.Status.FAILURE

class carry(pt.behaviour.Behaviour):
    def __init__(self, robot_id):
        super(carry, self).__init__("carry?")
        self.robot_id = robot_id

    def update(self) -> pt.common.Status:
        if not ge_info['reached']:
            return pt.common.Status.FAILURE
        mission_id = ge_info['mission_todo']
        mission_type = mission_list[mission_id].type
        if mission_type == 2:
            ge_info['is_mission'][2] = True
            return pt.common.Status.SUCCESS
        return pt.common.Status.FAILURE

class is_blocked(pt.behaviour.Behaviour):
    def __init__(self, robot_id):
        super(is_blocked, self).__init__("is blocked")
        self.robot_id = robot_id

    def update(self) -> pt.common.Status:
        if not ge_info['robot_state'] == 'Ready' or ge_info['mission_todo'] == -1 or ge_info['is_blocked_by'] == -1:
            return pt.common.Status.FAILURE
        else:
            ge_info['blocked'] = True
            return pt.common.Status.SUCCESS

class reach_mission(pt.behaviour.Behaviour):
    def __init__(self, robot_id):
        super(reach_mission, self).__init__("reach mission")
        self.robot_id = robot_id

    def update(self) -> pt.common.Status:
        if not ge_info['robot_state'] == 'Ready' or ge_info['mission_todo'] == -1:
            return pt.common.Status.FAILURE
        target_location = mission_list[ge_info['mission_todo']].location
        if ge_info['current_location'] == target_location:
            ge_info['reached'] = True
            return pt.common.Status.SUCCESS
        else:
            return pt.common.Status.FAILURE

class execute_mission(pt.behaviour.Behaviour):
    def __init__(self, robot_id, mission_type: int):
        super(execute_mission, self).__init__("execute mission")
        self.robot_id = robot_id
        self.mission_type = mission_type

    def update(self) -> pt.common.Status:
        if not ge_info['reached'] or not ge_info['is_mission'][self.mission_type]:
            return pt.common.Status.FAILURE
        mission = mission_list[ge_info['mission_todo']]
        ability_value = custom_behaviours.ability[self.robot_id][mission.type]
        time_cost = (3 - ability_value / 5) * mission.b
        energy_cost = time_cost * mission.a
        remain_energy_percent = (ge_info['current_energy'] - energy_cost) / INITIAL_ENERGY
        ge_info['current_energy'] -= energy_cost
        ge_info['total_time_cost'] += time_cost
        # 计算当前任务得分
        if not mission.time_limit == 0:
            # 时间窗口剩余时间越少，得分越低，执行任务时间超过了时间窗口，则不得分
            if mission.time_limit - ge_info['total_time_cost'] >= 0:
                score = mission.time_limit - ge_info['total_time_cost']
            else:
                score = 0
        else:
            score = mission.priority
        ge_info['total_score'] += score
        mission_list[ge_info['mission_todo']].state = mission_states[2]
        ge_info['accomplished_missions'].append(ge_info['mission_todo'])
        ge_info['execute_success'] = True
        # 完成1个任务后临时的状态变量应初始化
        ge_info['mission_todo'] = -1
        ge_info['reached'] = False
        ge_info['robot_state'] = 'No Check'
        ge_info['is_mission'][self.mission_type] = False
        ge_info['mission_counts'] += 1
        if ge_info['mission_counts'] >= len(custom_behaviours.allocated_missions[self.robot_id]):
            ge_info['mission_counts'] = 0
        return pt.common.Status.SUCCESS