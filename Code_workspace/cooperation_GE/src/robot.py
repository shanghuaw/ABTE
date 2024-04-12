import random

ENERGY_FACTOR = 5  # 焦耳/米
INITIAL_ENERGY = 20000.0  # 焦耳
RUNNING_SPEED = 100  # 米/秒

class robot:
    def __init__(self, robot_type: int):
        self.type = robot_type
        # 系数a为执行任务单位时间消耗能量，b为时间系数，机器人能力值越小，所需时间越长
        if self.type == 0:
            self.ability = [10, 5, 5, 5]
        if self.type == 1:
            self.ability = [5, 10, 5, 5]
        if self.type == 2:
            self.ability = [5, 5, 10, 5]
        if self.type == 5:
            self.ability = [5, 5, 5, 10]
        # robot上报信息时会使得robot_information[0] = robot_id，service node读到robot_bid[0]不为空时即可记录相应的信息
        self.robot_information = [-1, [50, 50], INITIAL_ENERGY]
        self.is_blocked_by = -1
        self.robot_blocked = False
        self.total_path_cost = 0
        self.total_time_cost = 0.0
        self.total_score = 0.0
        self.allocated_missions = list()
        self.accomplished_missions = list()
        self.prior_missions = list()
        self.timeout_missions = list()
        self.mission_todo = -1
        self.robot_reached = -1
        self.mission_counts = 0
        self.robot_state = 'No Check'

robot_list = [robot(0), robot(1), robot(2), robot(5),
              robot(0), robot(1), robot(2), robot(5),
              robot(0), robot(1), robot(2), robot(5),
              robot(0), robot(1), robot(2), robot(5),
              robot(0), robot(1), robot(2), robot(5),
              robot(0), robot(1), robot(2), robot(5),
              robot(0), robot(1), robot(2), robot(5),
              robot(0), robot(1), robot(2), robot(5),
              robot(0), robot(1), robot(2), robot(5),
              robot(0), robot(1), robot(2), robot(5),
              robot(0), robot(1), robot(2), robot(5),
              robot(0), robot(1), robot(2), robot(5),
              robot(0), robot(1), robot(2), robot(5),
              robot(0), robot(1), robot(2), robot(5),
              robot(0), robot(1), robot(2), robot(5)]