import py_trees as pt
import threading
import py_trees_interface
import robot
from time import sleep, time
from mission import mission_list, mission_states
from robot import robot_list

# 当前实现逻辑是完成任务分配之后再统一开始执行，因此行为树只需要运行一遍，标志位无需重置
obstacle_range = [[15, 20, 10, 25], [50, 62, 60 ,75], [40, 58, 42, 48]]
mission_sorted = False  # 记录任务是否已按照优先级排序
mission_allocated = False  # 记录任务是否已完成分配
optional_states = ['No Check', 'Ready', 'Energy Deficiency', 'Component Damage', 'Offline']
current_GE_robot = -1  # 机器人串行占锁进化行为树

state_lock = threading.Lock()

def get_node_from_string(self, string):
    """
    Returns a py trees behavior or composite given the string
    """
    has_children = False
    if string == "Service":
        node = service(self.robot_id, self.robot_nums, self.mission_nums)
    elif string == "ReceiveNotification":
        node = receive_notification()
    elif string == "SendInformation":
        node = send_information(self.robot_id)
    elif string == "WaitAllocation":
        node = wait_allocation(self.robot_id)
    elif string == "GEForBTs":
        node = GE_For_BTs(self.robot_id, self.robot_nums, self.mission_nums)
    elif string == "CheckState":
        node = check_state(self.robot_id)
    elif string == "GetMission":
        node = get_mission(self.robot_id, self.mission_nums)
    elif string == "Rescue?":
        node = rescue(self.robot_id, self.mission_nums)
    elif string == "Excavation?":
        node = excavation(self.robot_id, self.mission_nums)
    elif string == "Carry?":
        node = carry(self.robot_id, self.mission_nums)
    elif string == "Search?":
        node = search(self.robot_id, self.mission_nums)
    elif string == "MoveToMission":
        node = move_to_mission(self.robot_id, self.mission_nums)
    elif string == "IsBlocked?":
        node = is_blocked(self.robot_id)
    elif string == "AvoidObstacle":
        node = avoid_obstacle(self.robot_id, self.mission_nums)
    elif string == "ReachMission?":
        node = reach_mission(self.robot_id, self.mission_nums)
    elif string == "ExecuteRescue":
        node = execute_mission(self.robot_id, self.mission_nums)
    elif string == "ExecuteExcavation":
        node = execute_mission(self.robot_id, self.mission_nums)
    elif string == "ExecuteCarry":
        node = execute_mission(self.robot_id, self.mission_nums)
    elif string == "ExecuteSearch":
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

class service(pt.behaviour.Behaviour):
    def __init__(self, robot_id, robot_nums, mission_nums):
        super(service, self).__init__("service")
        self.robot_id = robot_id
        self.robot_nums = robot_nums
        self.mission_nums = mission_nums

    def update(self):
        auction_thread = threading.Thread(target=auction, args=(self.robot_id,self.robot_nums,self.mission_nums,))
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
        robot_list[self.robot_id].robot_information[0] = self.robot_id
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
        mission_number = len(robot_list[self.robot_id].allocated_missions)
        if mission_number > 0:
            return pt.common.Status.SUCCESS
        else:
            return pt.common.Status.FAILURE

class GE_For_BTs(pt.behaviour.Behaviour):
    def __init__(self, robot_id, robot_nums, mission_nums):
        super(GE_For_BTs, self).__init__("GE For BTs")
        self.robot_id = robot_id
        self.robot_nums = robot_nums
        self.mission_nums = mission_nums

    def update(self):
        # global current_GE_robot
        # state_lock.acquire()
        # current_GE_robot = self.robot_id
        # print("current GE robot is", current_GE_robot)
        # print("allocated missions:", robot_list[self.robot_id].allocated_missions)
        # # init trackers
        # trackers.cache = {}
        # trackers.best_fitness_list = []
        # trackers.stats_list = []
        # trackers.best_ever = None
        # # Run evolution
        # individuals = params['SEARCH_LOOP']()
        # # Print final review
        # get_stats(individuals, end=True)
        # # initial mission state
        # for i in robot_list[self.robot_id].allocated_missions:
        #     mission_list[self.mission_nums][i].state = mission_states[0]
        # state_lock.release()
        # # Execute the best behaviour tree
        # execute_phenotype = trackers.best_ever.phenotype
        # execute_bt = py_trees_interface.PyTree(execute_phenotype, self.robot_id)
        global current_GE_robot
        state_lock.acquire()
        current_GE_robot = self.robot_id
        print("current execute robot is", current_GE_robot)
        print("allocated missions:", robot_list[self.robot_id].allocated_missions)
        state_lock.release()
        bt_string = "Seq_CheckState_GetMission_Sel_MoveToMission_Seq_IsBlocked?_AvoidObstacle_/Seq_/Sel_ReachMission?_" \
                    "Sel_Seq_Rescue?_ExecuteRescue_/Seq_Seq_Excavation?_ExecuteExcavation_/Seq_" \
                    "Seq_Carry?_ExecuteCarry_/Seq_Seq_Search?_ExecuteSearch_/Seq_/Sel_/Seq"
        execute_bt = py_trees_interface.PyTree(bt_string, self.robot_id, self.robot_nums, self.mission_nums)
        execute_bt.tick_bt(len(robot_list[self.robot_id].allocated_missions))
        return pt.common.Status.SUCCESS

def auction(robot_id, robot_nums, mission_nums):
    global mission_sorted
    global mission_allocated
    state_lock.acquire()
    if not mission_sorted:
        # step1: sort missions and notify
        # # 先按优先级排序
        # for i in range(0, mission_nums - 1):
        #     for j in range(0, mission_nums - i - 1):
        #         if mission_list[mission_nums][j].priority < mission_list[mission_nums][j + 1].priority:
        #             tmp = mission_list[mission_nums][j]
        #             mission_list[mission_nums][j] = mission_list[mission_nums][j + 1]
        #             mission_list[mission_nums][j + 1] = tmp
        # # 再按与出发点之间的距离排序
        # every_mission_num = int(mission_nums / 4)
        # for m in range(0, 4):
        #     for i in range(m * every_mission_num, every_mission_num * (1 + m) - 1):
        #         for j in range(m * every_mission_num, every_mission_num * (1 + m) - i - 1):
        #             former_distance = abs(mission_list[mission_nums][j].location[0] - 50) + abs(mission_list[mission_nums][j].location[1] - 50)
        #             latter_distance = abs(mission_list[mission_nums][j + 1].location[0] - 50) + abs(mission_list[mission_nums][j + 1].location[1] - 50)
        #             if former_distance > latter_distance:
        #                 tmp = mission_list[mission_nums][j]
        #                 mission_list[mission_nums][j] = mission_list[mission_nums][j + 1]
        #                 mission_list[mission_nums][j + 1] = tmp
        mission_sorted = True
        state_lock.release()
        print("robot{} sorted missions, mission list:".format(robot_id))
        for i in range(0, len(mission_list[mission_nums])):
            mission_list[mission_nums][i].show_info(i)
        # step2: receive information
        # 接收上报信息的停止条件是时间达到了预设值，或收到了所有上报信息
        bid_robots = list()
        end_time = time() + 1
        print("robot nums:", robot_nums)
        while time() < end_time and len(bid_robots) < robot_nums:
            for i in range(0, robot_nums):
                if robot_list[i].robot_information[0] == i and i not in bid_robots:
                    bid_robots.append(i)
                    print("receive robot{} information:{}".format(i, robot_list[i].robot_information))
        current_location = [[0, 0], [0, 0], [0, 0], [0, 0], [0, 0], [0, 0], [0, 0], [0, 0], [0, 0], [0, 0],
                            [0, 0], [0, 0], [0, 0], [0, 0], [0, 0], [0, 0], [0, 0], [0, 0], [0, 0], [0, 0],
                            [0, 0], [0, 0], [0, 0], [0, 0], [0, 0], [0, 0], [0, 0], [0, 0], [0, 0], [0, 0],
                            [0, 0], [0, 0], [0, 0], [0, 0], [0, 0], [0, 0], [0, 0], [0, 0], [0, 0], [0, 0],
                            [0, 0], [0, 0], [0, 0], [0, 0], [0, 0], [0, 0], [0, 0], [0, 0], [0, 0], [0, 0],
                            [0, 0], [0, 0], [0, 0], [0, 0], [0, 0], [0, 0], [0, 0], [0, 0], [0, 0], [0, 0]]
        current_energy = [robot.INITIAL_ENERGY, robot.INITIAL_ENERGY, robot.INITIAL_ENERGY, robot.INITIAL_ENERGY,
                          robot.INITIAL_ENERGY, robot.INITIAL_ENERGY, robot.INITIAL_ENERGY, robot.INITIAL_ENERGY,
                          robot.INITIAL_ENERGY, robot.INITIAL_ENERGY, robot.INITIAL_ENERGY, robot.INITIAL_ENERGY,
                          robot.INITIAL_ENERGY, robot.INITIAL_ENERGY, robot.INITIAL_ENERGY, robot.INITIAL_ENERGY,
                          robot.INITIAL_ENERGY, robot.INITIAL_ENERGY, robot.INITIAL_ENERGY, robot.INITIAL_ENERGY,
                          robot.INITIAL_ENERGY, robot.INITIAL_ENERGY, robot.INITIAL_ENERGY, robot.INITIAL_ENERGY,
                          robot.INITIAL_ENERGY, robot.INITIAL_ENERGY, robot.INITIAL_ENERGY, robot.INITIAL_ENERGY,
                          robot.INITIAL_ENERGY, robot.INITIAL_ENERGY, robot.INITIAL_ENERGY, robot.INITIAL_ENERGY,
                          robot.INITIAL_ENERGY, robot.INITIAL_ENERGY, robot.INITIAL_ENERGY, robot.INITIAL_ENERGY,
                          robot.INITIAL_ENERGY, robot.INITIAL_ENERGY, robot.INITIAL_ENERGY, robot.INITIAL_ENERGY,
                          robot.INITIAL_ENERGY, robot.INITIAL_ENERGY, robot.INITIAL_ENERGY, robot.INITIAL_ENERGY,
                          robot.INITIAL_ENERGY, robot.INITIAL_ENERGY, robot.INITIAL_ENERGY, robot.INITIAL_ENERGY,
                          robot.INITIAL_ENERGY, robot.INITIAL_ENERGY, robot.INITIAL_ENERGY, robot.INITIAL_ENERGY,
                          robot.INITIAL_ENERGY, robot.INITIAL_ENERGY, robot.INITIAL_ENERGY, robot.INITIAL_ENERGY,
                          robot.INITIAL_ENERGY, robot.INITIAL_ENERGY, robot.INITIAL_ENERGY, robot.INITIAL_ENERGY,]
        current_time_cost = [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0,
                             0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0,
                             0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0,
                             0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0,
                             0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0,
                             0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]
        path_time = [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0,
                     0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0,
                     0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0,
                     0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0,
                     0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0,
                     0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]
        execute_time = [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0,
                        0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0,
                        0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0,
                        0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0,
                        0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0,
                        0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]
        for i in range(0, mission_nums):
            bid_value = [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0,
                         0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0,
                         0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0,
                         0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0,
                         0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0,
                         0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]
            max_bid_value = 0.0
            max_robot_id = -1
            robot_energy_cost = 0
            # step3: calculate bids
            for robot_id in bid_robots:
                path_cost = (abs(mission_list[mission_nums][i].location[0] - current_location[robot_id][0]) +
                             abs(mission_list[mission_nums][i].location[1] - current_location[robot_id][1]))
                ability_value = robot_list[robot_id].ability[mission_list[mission_nums][i].type]
                # 路上的时间 + 执行任务所需时间
                path_time[robot_id] = path_cost / robot.RUNNING_SPEED
                # execute_time[robot_id] = mission_list[mission_nums][i].b * (2 - ability_value / 10)
                execute_time[robot_id] = mission_list[mission_nums][i].b / ability_value
                # 路上的能量消耗 + 执行任务能量消耗
                energy_cost = robot.ENERGY_FACTOR * path_cost + mission_list[mission_nums][i].a * execute_time[robot_id]
                remain_energy_percent = (current_energy[robot_id] - energy_cost) / robot.INITIAL_ENERGY
                # 执行任务后剩余能量小于5%则不参与当前任务拍卖
                if remain_energy_percent < 0.05:
                    print("robot{} quit mission, energy cost:{}, remain energy:{:.2%}".format(
                        robot_id, energy_cost, remain_energy_percent))
                    continue
                # bid_value[robot_id] = remain_energy_percent * 100 / (current_time_cost[robot_id] +
                #                                                      path_time[robot_id] + execute_time[robot_id])
                bid_value[robot_id] = remain_energy_percent * 100 / (path_time[robot_id] + execute_time[robot_id])
                print("robot{}, path_time:{}, execute_time:{}, remain_energy:{:.2%}, bid_vlaue:{}".format(
                    robot_id, path_time[robot_id], execute_time[robot_id], remain_energy_percent, bid_value[robot_id]))
                if bid_value[robot_id] > max_bid_value:
                    max_bid_value = bid_value[robot_id]
                    max_robot_id = robot_id
                    robot_energy_cost = energy_cost
            # step4: allocate mission
            mission_list[mission_nums][i].show_info(i)
            print("**************** robot{} max bid value is {} ****************".format(max_robot_id, max_bid_value))
            # 有机器人中标，将任务放入已分配列表
            if not max_robot_id == -1:
                robot_list[max_robot_id].allocated_missions.append(i)
                current_location[max_robot_id] = mission_list[mission_nums][i].location
                current_energy[max_robot_id] -= robot_energy_cost
                current_time_cost[max_robot_id] += path_time[max_robot_id] + execute_time[max_robot_id]
        mission_allocated = True
        for i in range(0, robot_nums):
            print("\n**************** robot{} mission list: ****************".format(i))
            for j in robot_list[i].allocated_missions:
                mission_list[mission_nums][j].show_info(j)
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

    def update(self) -> pt.common.Status:
        if not robot_list[self.robot_id].robot_state == 'Ready' or robot_list[self.robot_id].mission_todo == -1:
            return pt.common.Status.FAILURE
        current_location = robot_list[self.robot_id].robot_information[1]
        mission_id = robot_list[self.robot_id].mission_todo
        target_location = mission_list[self.mission_nums][mission_id].location
        path_cost = 0
        while not current_location == target_location:
            # 机器人在移动的过程中遇到了障碍物，则返回失败，进行避障操作
            robot_list[self.robot_id].is_blocked_by = in_range(current_location, obstacle_range)
            if not robot_list[self.robot_id].is_blocked_by == -1:
                energy_cost = robot.ENERGY_FACTOR * path_cost
                robot_list[self.robot_id].robot_information[2] -= energy_cost
                robot_list[self.robot_id].total_path_cost += path_cost
                robot_list[self.robot_id].total_time_cost += path_cost / robot.RUNNING_SPEED
                robot_list[self.robot_id].robot_information[1] = current_location
                print("robot{} move to mission{}, blocked by {}, current location:{}".format(
                    self.robot_id, mission_id, robot_list[self.robot_id].is_blocked_by, current_location))
                sleep(path_cost / robot.RUNNING_SPEED / 50)
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
        energy_cost = robot.ENERGY_FACTOR * path_cost
        robot_list[self.robot_id].robot_information[2] -= energy_cost
        robot_list[self.robot_id].total_path_cost += path_cost
        robot_list[self.robot_id].total_time_cost += path_cost / robot.RUNNING_SPEED
        robot_list[self.robot_id].robot_information[1] = current_location
        print("robot{} move to mission{}, isn't blocked, current location:{}, total path cost:{}, remain energy:{}".
              format(self.robot_id, mission_id, current_location,
                     robot_list[self.robot_id].total_path_cost, robot_list[self.robot_id].robot_information[2]))
        sleep(path_cost / robot.RUNNING_SPEED / 50)
        return pt.common.Status.SUCCESS

class avoid_obstacle(pt.behaviour.Behaviour):
    def __init__(self, robot_id, mission_nums):
        super(avoid_obstacle, self).__init__("avoid obstacle")
        self.robot_id = robot_id
        self.mission_nums = mission_nums

    def update(self) -> pt.common.Status:
        if not robot_list[self.robot_id].robot_state == 'Ready' or not robot_list[self.robot_id].robot_blocked:
            return pt.common.Status.FAILURE
        current_location = robot_list[self.robot_id].robot_information[1]
        mission_id = robot_list[self.robot_id].mission_todo
        target_location = mission_list[self.mission_nums][mission_id].location
        obstacle_id = robot_list[self.robot_id].is_blocked_by
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
        robot_list[self.robot_id].robot_blocked = False
        robot_list[self.robot_id].is_blocked_by = -1
        robot_list[self.robot_id].robot_information[1] = current_location
        # 移动过程中的能量、时间消耗忽略不计
        energy_cost = robot.ENERGY_FACTOR * path_cost
        robot_list[self.robot_id].robot_information[2] -= energy_cost
        robot_list[self.robot_id].total_path_cost += path_cost
        robot_list[self.robot_id].total_time_cost += path_cost / robot.RUNNING_SPEED
        print("after avoid obstacle, current_location:{}".format(current_location))
        sleep(path_cost / robot.RUNNING_SPEED / 50)
        return pt.common.Status.SUCCESS

class check_state(pt.behaviour.Behaviour):
    def __init__(self, robot_id):
        super(check_state, self).__init__("check state")
        self.robot_id = robot_id
        robot_list[self.robot_id].robot_state = 'No Check'

    def update(self) -> pt.common.Status:
        robot_list[self.robot_id].robot_state = 'Ready'
        if robot_list[self.robot_id].robot_information[2] / robot.INITIAL_ENERGY <= 0.1:
            print("robot{} remain energy percent is less than 10%, check state failure".format(self.robot_id))
            return pt.common.Status.FAILURE
        return pt.common.Status.SUCCESS

class get_mission(pt.behaviour.Behaviour):
    def __init__(self, robot_id, mission_nums):
        super(get_mission, self).__init__("get mission")
        self.robot_id = robot_id
        self.mission_nums = mission_nums

    def update(self) -> pt.common.Status:
        if not robot_list[self.robot_id].is_blocked_by == -1:
            return pt.common.Status.SUCCESS
        if not robot_list[self.robot_id].robot_state == 'Ready':
            return pt.common.Status.FAILURE
        mission_sums = len(robot_list[self.robot_id].allocated_missions)
        current_location = robot_list[self.robot_id].robot_information[1]
        while robot_list[self.robot_id].mission_counts < mission_sums:
            mission_id = robot_list[self.robot_id].allocated_missions[robot_list[self.robot_id].mission_counts]
            mission_state = mission_list[self.mission_nums][mission_id].state
            if not mission_state == mission_states[0]:
                robot_list[self.robot_id].mission_counts += 1
                if robot_list[self.robot_id].mission_counts >= mission_sums:
                    robot_list[self.robot_id].mission_counts = 0
                continue
            mission_type = mission_list[self.mission_nums][mission_id].type
            if mission_type == 0 or mission_type == 1:
                break
            mission_location = mission_list[self.mission_nums][mission_id].location
            mission_distance = (abs(mission_location[0] - current_location[0]) +
                               abs(mission_location[1] - current_location[1]))
            record_counts = robot_list[self.robot_id].mission_counts
            for i in range(mission_sums - 1, -1, -1):
                mission_compared = robot_list[self.robot_id].allocated_missions[i]
                if not mission_list[self.mission_nums][mission_compared].type == 2:
                    break
                if not mission_compared == mission_id and mission_list[self.mission_nums][mission_compared].state == mission_states[0]:
                    distance = (abs(mission_list[self.mission_nums][mission_compared].location[0] - current_location[0]) +
                               abs(mission_list[self.mission_nums][mission_compared].location[1] - current_location[1]))
                    # 准备执行的任务不是距当前位置最近的任务，则找下一个任务
                    if distance < mission_distance:
                        robot_list[self.robot_id].mission_counts += 1
                        if robot_list[self.robot_id].mission_counts >= mission_sums:
                            robot_list[self.robot_id].mission_counts = 0
                        break
            if robot_list[self.robot_id].mission_counts == record_counts:
                break
        robot_list[self.robot_id].mission_todo = \
            robot_list[self.robot_id].allocated_missions[robot_list[self.robot_id].mission_counts]
        return pt.common.Status.SUCCESS

class is_blocked(pt.behaviour.Behaviour):
    def __init__(self, robot_id):
        super(is_blocked, self).__init__("is blocked?")
        self.robot_id = robot_id

    def update(self) -> pt.common.Status:
        if not robot_list[self.robot_id].is_blocked_by == -1:
            robot_list[self.robot_id].robot_blocked = True
            return pt.common.Status.SUCCESS
        else:
            return pt.common.Status.FAILURE

class reach_mission(pt.behaviour.Behaviour):
    def __init__(self, robot_id, mission_nums):
        super(reach_mission, self).__init__("reach mission")
        self.robot_id = robot_id
        self.mission_nums = mission_nums

    def update(self) -> pt.common.Status:
        current_location = robot_list[self.robot_id].robot_information[1]
        mission_id = robot_list[self.robot_id].mission_todo
        target_location = mission_list[self.mission_nums][mission_id].location
        if current_location == target_location:
            robot_list[self.robot_id].robot_reached = True
            print("robot{} reach mission{}, ready for executing".format(self.robot_id, mission_id))
            return pt.common.Status.SUCCESS
        else:
            return pt.common.Status.FAILURE

class rescue(pt.behaviour.Behaviour):
    def __init__(self, robot_id, mission_nums):
        super(rescue, self).__init__("rescue?")
        self.robot_id = robot_id
        self.mission_nums = mission_nums

    def update(self) -> pt.common.Status:
        mission_id = robot_list[self.robot_id].mission_todo
        mission_type = mission_list[self.mission_nums][mission_id].type
        if mission_type == 0:
            return pt.common.Status.SUCCESS
        return pt.common.Status.FAILURE

class excavation(pt.behaviour.Behaviour):
    def __init__(self, robot_id, mission_nums):
        super(excavation, self).__init__("excavation?")
        self.robot_id = robot_id
        self.mission_nums = mission_nums

    def update(self) -> pt.common.Status:
        mission_id = robot_list[self.robot_id].mission_todo
        mission_type = mission_list[self.mission_nums][mission_id].type
        if mission_type == 1:
            return pt.common.Status.SUCCESS
        return pt.common.Status.FAILURE

class carry(pt.behaviour.Behaviour):
    def __init__(self, robot_id, mission_nums):
        super(carry, self).__init__("carry?")
        self.robot_id = robot_id
        self.mission_nums = mission_nums

    def update(self) -> pt.common.Status:
        mission_id = robot_list[self.robot_id].mission_todo
        mission_type = mission_list[self.mission_nums][mission_id].type
        if mission_type == 2:
            return pt.common.Status.SUCCESS
        return pt.common.Status.FAILURE

class search(pt.behaviour.Behaviour):
    def __init__(self, robot_id, mission_nums):
        super(search, self).__init__("search?")
        self.robot_id = robot_id
        self.mission_nums = mission_nums

    def update(self) -> pt.common.Status:
        mission_id = robot_list[self.robot_id].mission_todo
        mission_type = mission_list[self.mission_nums][mission_id].type
        if mission_type == 3:
            return pt.common.Status.SUCCESS
        return pt.common.Status.FAILURE

class execute_mission(pt.behaviour.Behaviour):
    def __init__(self, robot_id, mission_nums):
        super(execute_mission, self).__init__("execute mission")
        self.robot_id = robot_id
        self.mission_nums = mission_nums

    def update(self) -> pt.common.Status:
        if not robot_list[self.robot_id].robot_reached:
            return pt.common.Status.FAILURE
        mission_id = robot_list[self.robot_id].mission_todo
        mission = mission_list[self.mission_nums][mission_id]
        ability_value = robot_list[self.robot_id].ability[mission.type]
        # time_cost = (2 - ability_value / 10) * mission.b
        time_cost = mission.b / ability_value
        energy_cost = time_cost * mission.a
        remain_energy_percent = (robot_list[self.robot_id].robot_information[2] - energy_cost) / robot.INITIAL_ENERGY
        # 如果执行任务之后剩余能量小于5%，则不执行当前任务
        if remain_energy_percent < 0.05:
            print("robot{} remain energy will be {:.2%} after executing mission{}, failure".format(
                self.robot_id, remain_energy_percent, mission_id))
            return pt.common.Status.FAILURE
        robot_list[self.robot_id].robot_information[2] -= energy_cost
        robot_list[self.robot_id].total_time_cost += time_cost
        sleep(time_cost / 100)
        # 记录任务完成情况
        if not mission.time_limit == 0:
            if mission.time_limit - robot_list[self.robot_id].total_time_cost >= 0:
                score = mission.priority * (3 - mission.type)
                mission_list[self.mission_nums][mission_id].state = mission_states[2]
                robot_list[self.robot_id].accomplished_missions.append(mission_id)
                robot_list[self.robot_id].prior_missions.append(mission_id)
            else:
                score = 0
                mission_list[self.mission_nums][mission_id].state = mission_states[1]
                robot_list[self.robot_id].timeout_missions.append(mission_id)
        else:
            score = mission.priority
            mission_list[self.mission_nums][mission_id].state = mission_states[2]
            robot_list[self.robot_id].accomplished_missions.append(mission_id)
        print("robot{} mission{} score:{}".format(self.robot_id, mission_id, score))
        robot_list[self.robot_id].total_score += score
        # 完成1个任务后临时的状态变量应初始化
        robot_list[self.robot_id].mission_todo = -1
        robot_list[self.robot_id].robot_reached = False
        robot_list[self.robot_id].robot_state = 'No Check'
        robot_list[self.robot_id].mission_counts += 1
        if robot_list[self.robot_id].mission_counts >= len(robot_list[self.robot_id].allocated_missions):
            robot_list[self.robot_id].mission_counts = 0
        print("robot{} mission{} accomplished".format(self.robot_id, mission_id))
        return pt.common.Status.SUCCESS