import py_trees as pt
import random
from time import sleep, time
import threading
from stats.stats import get_stats
from algorithm.parameters import params
import py_trees_interface
from utilities.stats import trackers

task_location = [0, 0]
task_changed = [False, False, False]
# 记录中标的robot id
chosen_robot = -1
# robot上报信息时会使得robot_information[robot_name][0] = robot_name，service node读到robot_bid[0]不为空时即可记录相应的信息
robot_information = [[-1, [0, 0], 10000.0, 20], [-1, [0, 50], 8000.0, 20], [-1, [50, 50], 6000.0, 20]]
initial_energy = [10000.0, 8000.0, 7000.0]
total_path_cost = [0, 0, 0]
total_time_cost = [0.0, 0.0, 0.0]
energy_factor = 15  # 乘以路程得到能量消耗
max_tasks = 100  # 执行任务数量上限
max_fails = 10  # 分配任务失败上限
task_completes = [0, 0, 0]  # 各robot执行成功任务数量
task_fails = [0, 0, 0]  # 各robot执行失败任务数量
global robot_state  # 执行任务之前检查机器人的状态
optional_states = ['No Check', 'Ready', 'Energy Deficiency', 'Component Damage', 'Offline']
# x范围[0,50]，y范围[0,50]，随机生成的100个max_tasks个任务坐标
task_locations = [[47, 13], [45, 14], [43, 7], [30, 32], [23, 4], [27, 33], [34, 41], [33, 45], [29, 44], [27, 50],
                  [38, 8], [21, 42], [10, 29], [37, 27], [14, 20], [11, 29], [13, 3], [34, 15], [48, 47], [23, 23],
                  [47, 15], [7, 21], [20, 24], [0, 16], [15, 28], [3, 31], [48, 34], [31, 35], [13, 18], [3, 42],
                  [22, 28], [2, 39], [37, 22], [28, 38], [23, 7], [3, 9], [41, 41], [45, 10], [13, 9], [8, 26],
                  [21, 25], [35, 20], [44, 13], [12, 48], [35, 48], [19, 35], [8, 22], [33, 1], [19, 22], [49, 7],
                  [16, 29], [39, 32], [11, 39], [40, 33], [0, 6], [10, 31], [31, 26], [10, 28], [8, 37], [34, 49],
                  [29, 31], [38, 18], [36, 1], [7, 40], [31, 34], [42, 0], [17, 46], [20, 37], [28, 38], [21, 11],
                  [4, 47], [49, 26], [38, 32], [50, 9], [1, 43], [34, 2], [13, 26], [27, 0], [5, 18], [2, 13],
                  [15, 18], [1, 8], [45, 29], [23, 5], [21, 18], [34, 40], [29, 45], [14, 40], [27, 15], [13, 8],
                  [43, 13], [1, 46], [43, 43], [9, 48], [12, 24], [13, 7], [35, 1], [4, 49], [4, 3], [33, 25]]

state_lock = threading.Lock()

def get_node_from_string(self, string):
    """
    Returns a py trees behavior or composite given the string
    """
    has_children = False
    if string == "Service":
        node = service(self.robot_id)
    elif string == "ReceiveTask":
        node = receive_task()
    elif string == "SendInformation":
        node = send_information(self.robot_id)
    elif string == "WaitAssign":
        node = wait_assign(self.robot_id)
    elif string == "ExecuteTask":
        node = execute_task(self.robot_id)
    elif string == "GEforBTs":
        node = GE_for_BTs(self.robot_id)
    elif string == "CheckState":
        node = check_state(self.robot_id)
    elif string == "simExecuteTask":
        node = simulate_execute_task(self.robot_id)
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

class receive_task(pt.behaviour.Behaviour):
    def __init__(self):
        super(receive_task, self).__init__("receive task")

    def update(self):
        while True:
            if True in task_changed:
                break
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

class wait_assign(pt.behaviour.Behaviour):
    def __init__(self, robot_id):
        super(wait_assign, self).__init__("wait assign")
        self.robot_id = robot_id

    def update(self):
        while True:
            if chosen_robot != -1:
                break
        # 收到任务分配结果后，初始化状态上报通知标志位，以及任务位置是否刷新标志位
        state_lock.acquire()
        robot_information[self.robot_id][0] = -1
        task_changed[self.robot_id] = False
        state_lock.release()
        if  self.robot_id == chosen_robot:
            return pt.common.Status.SUCCESS
        else:
            return pt.common.Status.FAILURE

class execute_task(pt.behaviour.Behaviour):
    def __init__(self, robot_id):
        super(execute_task, self).__init__("execute task")
        self.robot_id = robot_id

    def update(self):
        path_cost = abs(task_location[0] - robot_information[self.robot_id][1][0]) + \
                    abs(task_location[1] - robot_information[self.robot_id][1][1])
        time_cost = path_cost / robot_information[self.robot_id][3]
        total_path_cost[self.robot_id] += path_cost
        total_time_cost[self.robot_id] += time_cost
        energy_cost = energy_factor * path_cost
        remain_energy_percent = (robot_information[self.robot_id][2] - energy_cost) / initial_energy[self.robot_id]
        if remain_energy_percent >= 0.05:
            state_lock.acquire()
            robot_information[self.robot_id][1] = task_location
            robot_information[self.robot_id][2] = robot_information[self.robot_id][2] - energy_cost
            task_completes[self.robot_id] += 1
            state_lock.release()
            return pt.common.Status.SUCCESS
        else:
            print("remain energy is not enough to execute task")
            return pt.common.Status.FAILURE

class GE_for_BTs(pt.behaviour.Behaviour):
    def __init__(self, robot_id):
        super(GE_for_BTs, self).__init__("GE for BTs")
        self.robot_id = robot_id

    def update(self):
        # Run evolution
        individuals = params['SEARCH_LOOP']()
        # Print final review
        get_stats(individuals, end=True)
        # Execute the best behaviour tree
        execute_phenotype = trackers.best_ever.phenotype.replace('sim', '')
        execute_bt = py_trees_interface.PyTree(execute_phenotype, self.robot_id)
        execute_bt.tick_bt()
        return pt.common.Status.SUCCESS

class check_state(pt.behaviour.Behaviour):
    def __init__(self, robot_id):
        super(check_state, self).__init__("check state")
        self.robot_id = robot_id
        py_trees_interface.sim_execute_task = False
        global robot_state
        robot_state = optional_states[0]

    def update(self):
        global robot_state
        robot_state = optional_states[1]
        return pt.common.Status.SUCCESS

class simulate_execute_task(pt.behaviour.Behaviour):
    def __init__(self, robot_id):
        super(simulate_execute_task, self).__init__("simulate execute task")
        self.robot_id = robot_id
        global robot_state
        robot_state = optional_states[0]

    def update(self):
        global robot_state
        if robot_state == optional_states[1]:
            py_trees_interface.path_cost = abs(task_location[0] - robot_information[self.robot_id][1][0]) +\
                        abs(task_location[1] - robot_information[self.robot_id][1][1])
            py_trees_interface.time_cost = py_trees_interface.path_cost / robot_information[self.robot_id][3]
            py_trees_interface.sim_execute_task = True
            return pt.common.Status.SUCCESS
        else:
            return pt.common.Status.FAILURE

def auction(robot_id):
    # step0: init
    global task_changed
    global chosen_robot
    global task_location
    bid_state = [False, False, False]
    bid_value = [0.0, 0.0, 0.0]
    # step1: find task
    sleep(1)
    state_lock.acquire()
    release_lock = False
    chosen_robot = -1
    if True not in task_changed:
        # task_location = [random.randint(0, 50), random.randint(0, 50)]
        completed_sums = 0
        for i in range(0, 3):
            completed_sums += task_completes[i]
        failed_sums = max(task_fails[0], task_fails[1], task_fails[2])
        if completed_sums + failed_sums < max_tasks:
            task_location = task_locations[completed_sums + failed_sums]
        else:
            task_location = task_locations[completed_sums + failed_sums - 1]
        print("robot%d find task," % robot_id, "location is", task_location)
        # step2: notify
        task_changed[robot_id] = True
        release_lock = True
        state_lock.release()
        # step3: receive informations
        # 接收上报信息的停止条件是时间达到了预设值，或收到了所有上报信息
        bid_robots = list()
        end_time = time() + 1
        while time() < end_time and False in bid_state:
            if robot_information[0][0] == 0 and not bid_state[0]:
                bid_state[0] = True
                bid_robots.append(0)
                print("receive robot0 information:", robot_information[0])
            if robot_information[1][0] == 1 and not bid_state[1]:
                bid_state[1] = True
                bid_robots.append(1)
                print("receive robot1 information:", robot_information[1])
            if robot_information[2][0] == 2 and not bid_state[2]:
                bid_state[2] = True
                bid_robots.append(2)
                print("receive robot2 information:", robot_information[2])
        # step4: calculate bids
        max_bid_value = 0
        max_robot_id = -1
        for robot_id in bid_robots:
            path_cost = abs(task_location[0] - robot_information[robot_id][1][0]) + \
                abs(task_location[1] - robot_information[robot_id][1][1])
            time_cost = path_cost / robot_information[robot_id][3]
            energy_cost = energy_factor * path_cost
            remain_energy_percent = (robot_information[robot_id][2] - energy_cost) / initial_energy[robot_id]
            #print("robot_id:%d, path_cost:%d, time_cost:%f, energy_cost:%f, remain_energy:%f" % (robot_id, path_cost, time_cost, energy_cost, remain_energy))
            # step5: assign task
            sleep(1)
            # 执行任务后剩余能量小于5%则不执行任务
            if remain_energy_percent < 0.05:
                print("robot{} quit task, energy cost:{}, remain energy:{:.2%}".format(
                    robot_id, energy_cost, remain_energy_percent))
                continue
            if path_cost != 0:
                bid_value[robot_id] = remain_energy_percent / time_cost
                print("robot{}, energy cost:{}, remain energy:{:.2%}, bid value:{}".format(
                    robot_id, energy_cost, remain_energy_percent, bid_value[robot_id]))
                if bid_value[robot_id] > max_bid_value:
                    max_bid_value = bid_value[robot_id]
                    max_robot_id = robot_id
            else:
                max_robot_id = robot_id
                break
        print("robot{} max bid value is {}".format(max_robot_id, max_bid_value))
        state_lock.acquire()
        # 所有机器人都无法执行任务，全体停止
        if max_robot_id == -1:
            chosen_robot = -2
        else:
            chosen_robot = max_robot_id
        state_lock.release()
    if not release_lock:
        state_lock.release()
    return