import py_trees as pt
from time import sleep, time
import threading
from mission import mission_list
import py_trees_interface
import ge_pt_interface


ENERGY_FACTOR = 8  # 乘以路程得到能量消耗
INITIAL_ENERGY = 10000.0
RUNNING_SPEED = 4

# 当前实现逻辑是完成任务分配之后再统一开始执行，因此行为树只需要运行一遍，标志位无需重置
# robot上报信息时会使得robot_information[robot_id][0] = robot_id，service node读到robot_bid[0]不为空时即可记录相应的信息
robot_information = [[-1, [0, 0], 10000.0], [-1, [0, 0], 10000.0], [-1, [0, 0], 10000.0]]
ability = [[10, 2, 6], [8, 10, 3], [9, 4, 10]]
obstacle_range = [[15, 30, 35, 46], [50, 62, 60 ,75], [76, 85, 21, 40]]
is_blocked_by = [-1, -1, -1]
robot_blocked = [False, False, False]
total_path_cost = [0, 0, 0]
total_time_cost = [0.0, 0.0, 0.0]
total_score = [0.0, 0.0, 0.0]
allocated_missions = [list(), list(), list()]
accomplished_missions = [list(), list(), list()]
mission_todo = [-1, -1, -1]
mission_sorted = False  # 记录任务是否已按照优先级排序
mission_allocated = False  # 记录任务是否已完成分配
robot_state = ['No Check', 'No Check', 'No Check']  # 执行任务之前检查机器人的状态
optional_states = ['No Check', 'Ready', 'Energy Deficiency', 'Component Damage', 'Offline']
current_GE_robot = -1  # 机器人串行占锁进化行为树
robot_reached = [False, False, False]
mission_counts = [0, 0, 0]

state_lock = threading.Lock()

def get_node_from_string(self, string):
    """
    Returns a py trees behavior or composite given the string
    """
    has_children = False
    if string == "Service":
        node = service(self.robot_id)
    elif string == "ReceiveNotification":
        node = receive_notification()
    elif string == "SendInformation":
        node = send_information(self.robot_id)
    elif string == "WaitAllocation":
        node = wait_allocation(self.robot_id)
    elif string == "GEForBTs":
        node = GE_For_BTs(self.robot_id)
    elif string == "CheckState":
        node = check_state(self.robot_id)
    elif string == "GetMission":
        node = get_mission(self.robot_id)
    elif string == "Rescue?":
        node = rescue(self.robot_id)
    elif string == "OutFire?":
        node = outfire(self.robot_id)
    elif string == "Carry?":
        node = carry(self.robot_id)
    elif string == "MoveToMission":
        node = move_to_mission(self.robot_id)
    elif string == "IsBlocked?":
        node = is_blocked(self.robot_id)
    elif string == "AvoidObstacle":
        node = avoid_obstacle(self.robot_id)
    elif string == "ReachMission?":
        node = reach_mission(self.robot_id)
    elif string == "ExecuteRescue":
        node = execute_mission(self.robot_id)
    elif string == "ExecuteOutFire":
        node = execute_mission(self.robot_id)
    elif string == "ExecuteCarry":
        node = execute_mission(self.robot_id)
    elif string == 'Sel':
        node = pt.composites.Selector("Selector", True)
        has_children = True
    elif string == 'Seq':
        node = pt.composites.Sequence("Sequence", True)
        has_children = True
    else:
        raise Exception("Unexpected character", string)

    return node, has_children

class service(pt.behaviour.Behaviour):
    def __init__(self, robot_id):
        super(service, self).__init__("service")
        self.robot_id = robot_id

    def update(self):
        auction_thread = threading.Thread(target=auction, args=(self.robot_id,))
        auction_thread.start()
        return pt.common.Status.SUCCESS

class receive_notification(pt.behaviour.Behaviour):
    def __init__(self):
        super(receive_notification, self).__init__("receive notification")

    def update(self):
        global mission_sorted
        while True:
            if mission_sorted:
                break
            sleep(0.05)
        return pt.common.Status.SUCCESS

class send_information(pt.behaviour.Behaviour):
    def __init__(self, robot_id):
        super(send_information, self).__init__("send information")
        self.robot_id = robot_id

    def update(self):
        state_lock.acquire()
        robot_information[self.robot_id][0] = self.robot_id
        state_lock.release()
        return pt.common.Status.SUCCESS

class wait_allocation(pt.behaviour.Behaviour):
    def __init__(self, robot_id):
        super(wait_allocation, self).__init__("wait allocation")
        self.robot_id = robot_id

    def update(self):
        while True:
            if mission_allocated:
                break
            sleep(0.05)
        mission_number = len(allocated_missions[self.robot_id])
        if mission_number > 0:
            return pt.common.Status.SUCCESS
        else:
            return pt.common.Status.FAILURE

class GE_For_BTs(pt.behaviour.Behaviour):
    def __init__(self, robot_id):
        super(GE_For_BTs, self).__init__("GE For BTs")
        self.robot_id = robot_id

    def update(self):
        bt_string = "Seq_CheckState_GetMission_Sel_PriorMission?_Seq_NeedExecute?_NearestMission?_/Seq_/Sel_" \
                    "NeedExecute?_Sel_MoveToMission_Seq_IsBlocked?_AvoidObstacle_/Seq_/Sel_ReachMission?_" \
                    "Sel_Seq_Rescue?_ExecuteRescue_/Seq_Seq_OutFire?_ExecuteOutFire_/Seq_Seq_Carry?_ExecuteCarry_/Seq_/Sel_/Seq"
        execute_bt = py_trees_interface.PyTree(bt_string, self.robot_id)
        execute_bt.tick_bt(len(allocated_missions[self.robot_id]))
        return pt.common.Status.SUCCESS

def auction(robot_id):
    global mission_sorted
    global mission_allocated
    mission_num = len(mission_list)
    state_lock.acquire()
    if not mission_sorted:
        # step1: sort missions and notify
        for i in range(0, mission_num - 1):
            for j in range(0, mission_num - i - 1):
                if mission_list[j].priority < mission_list[j + 1].priority:
                    tmp = mission_list[j]
                    mission_list[j] = mission_list[j + 1]
                    mission_list[j + 1] = tmp
        mission_sorted = True
        state_lock.release()
        print("robot{} sorted missions, mission list:".format(robot_id))
        for mission in mission_list:
            mission.show_info()
        # step2: receive information
        # 接收上报信息的停止条件是时间达到了预设值，或收到了所有上报信息
        bid_robots = list()
        end_time = time() + 1
        while time() < end_time and len(bid_robots) < 3:
            if robot_information[0][0] == 0 and 0 not in bid_robots:
                bid_robots.append(0)
                print("receive robot0 information:", robot_information[0])
            if robot_information[1][0] == 1 and 1 not in bid_robots:
                bid_robots.append(1)
                print("receive robot1 information:", robot_information[1])
            if robot_information[2][0] == 2 and 2 not in bid_robots:
                bid_robots.append(2)
                print("receive robot2 information:", robot_information[2])
        current_location = [[0, 0], [0, 0], [0, 0]]
        current_energy = [INITIAL_ENERGY, INITIAL_ENERGY, INITIAL_ENERGY]
        for i in range(0, mission_num):
            bid_value = [0.0, 0.0, 0.0]
            max_bid_value = 0.0
            max_robot_id = -1
            robot_energy_cost = 0
            # step3: calculate bids
            for robot_id in bid_robots:
                path_cost = abs(mission_list[i].location[0] - current_location[robot_id][0]) + \
                    abs(mission_list[i].location[1] - current_location[robot_id][1])
                ability_value = ability[robot_id][mission_list[i].type]
                # 路上的时间 + 执行任务所需时间
                path_time = path_cost / RUNNING_SPEED
                execute_time = mission_list[i].b * (2 - ability_value / 10)
                # 路上的能量消耗 + 执行任务能量消耗
                energy_cost = ENERGY_FACTOR * path_cost + mission_list[i].a * execute_time
                remain_energy_percent = (current_energy[robot_id] - energy_cost) / INITIAL_ENERGY
                # 执行任务后剩余能量小于5%则不参与当前任务拍卖
                if remain_energy_percent < 0.05:
                    print("robot{} quit mission, energy cost:{}, remain energy:{:.2%}".format(
                        robot_id, energy_cost, remain_energy_percent))
                    continue
                print("robot{}, path_cost:{}, execute_time:{}, energy_cost:{}, remain_energy:{:.2%}".format(
                    robot_id, path_cost, execute_time, energy_cost, remain_energy_percent))
                bid_value[robot_id] = (current_energy[robot_id] - energy_cost) / (path_time + execute_time)
                # bid_value[robot_id] = INITIAL_ENERGY / (path_time + execute_time) / energy_cost
                if bid_value[robot_id] > max_bid_value:
                    max_bid_value = bid_value[robot_id]
                    max_robot_id = robot_id
                    robot_energy_cost = energy_cost
            # step4: allocate mission
            mission_list[i].show_info()
            print("robot{} max bid value is {}".format(max_robot_id, max_bid_value))
            # 有机器人中标，将任务放入已分配列表
            if not max_robot_id == -1:
                allocated_missions[max_robot_id].append(i)
                current_location[max_robot_id] = mission_list[i].location
                current_energy[max_robot_id] -= robot_energy_cost
        mission_allocated = True
        for i in range(0, 3):
            print("robot{} mission list:".format(i))
            for j in allocated_missions[i]:
                mission_list[j].show_info()
    else:
        state_lock.release()
    return

def in_range(location, ranges):
    # nums为target_range数组大小
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
        if not robot_state[self.robot_id] == 'Ready' or mission_todo[self.robot_id] == -1:
            return pt.common.Status.FAILURE
        current_location = robot_information[self.robot_id][1]
        mission_id = mission_todo[self.robot_id]
        target_location = mission_list[mission_id].location
        path_cost = 0
        while not current_location == target_location:
            # 机器人在移动的过程中遇到了障碍物，则返回失败，进行避障操作
            is_blocked_by[self.robot_id] = in_range(current_location, obstacle_range)
            if not is_blocked_by[self.robot_id] == -1:
                energy_cost = ENERGY_FACTOR * path_cost
                robot_information[self.robot_id][2] -= energy_cost
                total_path_cost[self.robot_id] += path_cost
                total_time_cost[self.robot_id] += path_cost / RUNNING_SPEED
                robot_information[self.robot_id][1] = current_location
                print("robot{} move to mission{}, blocked by {}, current location:{}".format(
                    self.robot_id, mission_id, is_blocked_by[self.robot_id], current_location))
                sleep(path_cost / RUNNING_SPEED / 10)
                return pt.common.Status.FAILURE
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
        robot_information[self.robot_id][2] -= energy_cost
        total_path_cost[self.robot_id] += path_cost
        total_time_cost[self.robot_id] += path_cost / RUNNING_SPEED
        robot_information[self.robot_id][1] = current_location
        print("robot{} move to mission{}, isn't blocked, current location:{}, total path cost:{}, remain energy:{}".
              format(self.robot_id, mission_id, current_location,
                     total_path_cost[self.robot_id], robot_information[self.robot_id][2]))
        sleep(path_cost / RUNNING_SPEED / 10)
        return pt.common.Status.SUCCESS

class avoid_obstacle(pt.behaviour.Behaviour):
    def __init__(self, robot_id):
        super(avoid_obstacle, self).__init__("avoid obstacle")
        self.robot_id = robot_id

    def update(self) -> pt.common.Status:
        if not robot_state[self.robot_id] == 'Ready' or not robot_blocked[self.robot_id]:
            return pt.common.Status.FAILURE
        current_location = robot_information[self.robot_id][1]
        mission_id = mission_todo[self.robot_id]
        target_location = mission_list[mission_id].location
        obstacle_id = is_blocked_by[self.robot_id]
        path_cost = 0
        # 场景1：在矩形障碍物的宽边上，但不处于顶点
        if (current_location[0] == obstacle_range[obstacle_id][0] or
            current_location[0] == obstacle_range[obstacle_id][1]) and \
                not current_location[1] == obstacle_range[obstacle_id][2] and \
                not current_location[1] == obstacle_range[obstacle_id][3]:
            print("avoid obstacle, situation1")
            # 在x为常量的边， cost1为向下走，cost2为向上走
            cost1 = abs(obstacle_range[obstacle_id][2] - current_location[1]) +\
                    abs(current_location[0] - target_location[0]) +\
                    abs(obstacle_range[obstacle_id][2] - target_location[1])
            cost2 = abs(obstacle_range[obstacle_id][3] - current_location[1]) +\
                    abs(current_location[0] - target_location[0]) +\
                    abs(obstacle_range[obstacle_id][3] - target_location[1])
            if cost1 < cost2:
                # 向下走为最优路径
                path_cost += abs(obstacle_range[obstacle_id][2] - current_location[1])
                current_location[1] = obstacle_range[obstacle_id][2] - 1
            else:
                # 向上走为最优路径
                path_cost += abs(obstacle_range[obstacle_id][3] - current_location[1])
                current_location[1] = obstacle_range[obstacle_id][3] + 1
            # 如果目标点被障碍物完全挡住，则机器人还需要多绕一条边才算避障成功
            if obstacle_range[obstacle_id][2] <= \
                    target_location[1] <= obstacle_range[obstacle_id][3]:
                path_cost += abs(obstacle_range[obstacle_id][1] - obstacle_range[obstacle_id][0])
                if current_location[0] == obstacle_range[obstacle_id][0]:
                    current_location[0] = obstacle_range[obstacle_id][1] + 1
                else:
                    current_location[0] = obstacle_range[obstacle_id][0] - 1
        # 场景2：在矩形障碍物的长边上，但不处于顶点
        elif (current_location[1] == obstacle_range[obstacle_id][2] or
              current_location[1] == obstacle_range[obstacle_id][3]) and \
                  not current_location[0] == obstacle_range[obstacle_id][0] and \
                  not current_location[0] == obstacle_range[obstacle_id][1]:
            print("avoid obstacle, situation2")
            # 在y为常量的边，cost1为向左走，cost2为向右走
            cost1 = abs(obstacle_range[obstacle_id][0] - current_location[0]) +\
                    abs(current_location[1] - target_location[1]) +\
                    abs(obstacle_range[obstacle_id][0] - target_location[0])
            cost2 = abs(obstacle_range[obstacle_id][1] - current_location[0]) +\
                    abs(current_location[1] - target_location[1]) +\
                    abs(obstacle_range[obstacle_id][1] - target_location[0])
            if cost1 < cost2:
                # 向左走为最优路径
                path_cost += abs(obstacle_range[obstacle_id][0] - current_location[0])
                current_location[0] = obstacle_range[obstacle_id][0] - 1
            else:
                # 向右走为最优路径
                path_cost += abs(obstacle_range[obstacle_id][1] - current_location[0])
                current_location[0] = obstacle_range[obstacle_id][1] + 1
            # 如果目标点被障碍物完全挡住，则机器人还需要多绕一条边才算避障成功
            if obstacle_range[obstacle_id][0] <= \
                    target_location[0] <= obstacle_range[obstacle_id][1]:
                path_cost += abs(obstacle_range[obstacle_id][3] - obstacle_range[obstacle_id][2])
                if current_location[1] == obstacle_range[obstacle_id][2]:
                    current_location[1] = obstacle_range[obstacle_id][3] + 1
                else:
                    current_location[1] = obstacle_range[obstacle_id][2] - 1
        # 场景3：正好位于矩形障碍物的顶点上
        else:
            print("avoid obstacle, situation3")
            path_cost += (abs(current_location[0] - target_location[0]) + abs(current_location[1] - target_location[1]))
            current_location = target_location
        robot_blocked[self.robot_id] = False
        is_blocked_by[self.robot_id] = -1
        robot_information[self.robot_id][1] = current_location
        energy_cost = ENERGY_FACTOR * path_cost
        robot_information[self.robot_id][2] -= energy_cost
        total_path_cost[self.robot_id] += path_cost
        total_time_cost[self.robot_id] += path_cost / RUNNING_SPEED
        print("after avoid obstacle, current_location:{}".format(current_location))
        sleep(path_cost / RUNNING_SPEED / 10)
        return pt.common.Status.SUCCESS

class check_state(pt.behaviour.Behaviour):
    def __init__(self, robot_id):
        super(check_state, self).__init__("check state")
        self.robot_id = robot_id
        robot_state[self.robot_id] = 'No Check'

    def update(self) -> pt.common.Status:
        robot_state[self.robot_id] = 'Ready'
        if robot_information[self.robot_id][2] / INITIAL_ENERGY <= 0.1:
            print("robot{} remain energy percent is less than 10%, check state failure")
            return pt.common.Status.FAILURE
        return pt.common.Status.SUCCESS

class get_mission(pt.behaviour.Behaviour):
    def __init__(self, robot_id):
        super(get_mission, self).__init__("get mission")
        self.robot_id = robot_id

    def update(self) -> pt.common.Status:
        if not is_blocked_by[self.robot_id] == -1:
            return pt.common.Status.SUCCESS
        if not robot_state[self.robot_id] == 'Ready':
            return pt.common.Status.FAILURE
        if mission_counts[self.robot_id] < len(allocated_missions[self.robot_id]):
            mission_todo[self.robot_id] =\
                allocated_missions[self.robot_id][mission_counts[self.robot_id]]
            return pt.common.Status.SUCCESS
        else:
            print("robot{} no mission to execute".format(self.robot_id))
            return pt.common.Status.FAILURE

class is_blocked(pt.behaviour.Behaviour):
    def __init__(self, robot_id):
        super(is_blocked, self).__init__("is blocked?")
        self.robot_id = robot_id

    def update(self) -> pt.common.Status:
        if not is_blocked_by[self.robot_id] == -1:
            robot_blocked[self.robot_id] = True
            return pt.common.Status.SUCCESS
        else:
            return pt.common.Status.FAILURE

class reach_mission(pt.behaviour.Behaviour):
    def __init__(self, robot_id):
        super(reach_mission, self).__init__("reach mission")
        self.robot_id = robot_id

    def update(self) -> pt.common.Status:
        current_location = robot_information[self.robot_id][1]
        mission_id = mission_todo[self.robot_id]
        target_location = mission_list[mission_id].location
        if current_location == target_location:
            robot_reached[self.robot_id] = True
            print("robot{} reach mission{}, ready for executing".format(self.robot_id, mission_id))
            return pt.common.Status.SUCCESS
        else:
            return pt.common.Status.FAILURE

class rescue(pt.behaviour.Behaviour):
    def __init__(self, robot_id):
        super(rescue, self).__init__("rescue?")
        self.robot_id = robot_id

    def update(self) -> pt.common.Status:
        mission_id = mission_todo[self.robot_id]
        mission_type = mission_list[mission_id].type
        if mission_type == 0:
            return pt.common.Status.SUCCESS
        return pt.common.Status.FAILURE

class outfire(pt.behaviour.Behaviour):
    def __init__(self, robot_id):
        super(outfire, self).__init__("outfire?")
        self.robot_id = robot_id

    def update(self) -> pt.common.Status:
        mission_id = mission_todo[self.robot_id]
        mission_type = mission_list[mission_id].type
        if mission_type == 1:
            return pt.common.Status.SUCCESS
        return pt.common.Status.FAILURE

class carry(pt.behaviour.Behaviour):
    def __init__(self, robot_id):
        super(carry, self).__init__("carry?")
        self.robot_id = robot_id

    def update(self) -> pt.common.Status:
        mission_id = mission_todo[self.robot_id]
        mission_type = mission_list[mission_id].type
        if mission_type == 2:
            return pt.common.Status.SUCCESS
        return pt.common.Status.FAILURE

class execute_mission(pt.behaviour.Behaviour):
    def __init__(self, robot_id):
        super(execute_mission, self).__init__("execute mission")
        self.robot_id = robot_id

    def update(self) -> pt.common.Status:
        if not robot_reached[self.robot_id]:
            return pt.common.Status.FAILURE
        mission_id = mission_todo[self.robot_id]
        mission = mission_list[mission_id]
        ability_value = ability[self.robot_id][mission.type]
        time_cost = (2 - ability_value / 10) * mission.b
        energy_cost = time_cost * mission.a
        remain_energy_percent = (robot_information[self.robot_id][2] - energy_cost) / INITIAL_ENERGY
        # 如果执行任务之后剩余能量小于5%，则不执行当前任务
        if remain_energy_percent < 0.05:
            print("robot{} remain energy will be {:.2%} after executing mission{}, failure".format(
                self.robot_id, remain_energy_percent, mission_id))
            return pt.common.Status.FAILURE
        robot_information[self.robot_id][2] -= energy_cost
        total_time_cost[self.robot_id] += time_cost
        sleep(time_cost / 10)
        # 计算当前任务得分
        if not mission.time_limit == 0:
            # 时间窗口剩余时间越少，得分越低，执行任务时间超过了时间窗口，则不得分
            if mission.time_limit - total_time_cost[self.robot_id] >= 0:
                score = mission.s * (mission.time_limit - total_time_cost[self.robot_id])
            else:
                score = 0
        else:
            score = 2 * mission.b - time_cost
        print("robot{} mission{} score:{}".format(self.robot_id, mission_id, score))
        total_score[self.robot_id] += score
        state_lock.acquire()
        mission_list[mission_id].state = 'Accomplished'
        accomplished_missions[self.robot_id].append(mission_id)
        # 完成1个任务后临时的状态变量应初始化
        mission_todo[self.robot_id] = -1
        robot_reached[self.robot_id] = False
        robot_state[self.robot_id] = 'No Check'
        state_lock.release()
        print("robot{} mission{} accomplished".format(self.robot_id, mission_id))
        return pt.common.Status.SUCCESS