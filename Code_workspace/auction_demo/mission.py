import random

class mission:
    def __init__(self, mission_type: int, priority: int, location: list):
        self.type = mission_type
        self.priority = priority
        self.location = location
        self.state = mission_states[0]
        self.failure_robot = set()
        if self.type == 0:
            self.time_limit = (18 - self.priority) * 15
            self.a = 50
            self.b = 80
            self.s = 2.5
        if self.type == 1:
            self.time_limit = (12 - self.priority) * 18
            self.a = 60
            self.b = 40
            self.s = 1.5
        if self.type == 2:
            self.time_limit = 0
            self.a = 40
            self.b = 20
            self.s = 1

    def show_info(self):
        print("mission:{}  priority:{}  location:{}".format(
            mission_types[self.type], self.priority, self.location
        ))

mission_types = ['Rescue', 'OutFire', 'Transport']
mission_states = ['Idle', 'Underway', 'Accomplished']
mission_list = [mission(1, 5, [86, 6]), mission(2, 4, [96, 96]),
                mission(0, 10, [0, 50]), mission(2, 2, [63, 34]),
                mission(0, 8, [70, 33]), mission(1, 7, [84, 14]),
                mission(2, 3, [41, 6]), mission(2, 1, [72, 34]),
                mission(2, 2, [10, 13]), mission(1, 6, [52, 55])]

def generate_mission(number):
    missions = list()
    for i in range(0, number):
        mission_type = random.randint(0, 2)
        x = random.randint(0, 100)
        y = random.randint(0, 100)
        priority = 0
        if mission_type == 0:
            priority = random.randint(8, 10)
        if mission_type == 1:
            priority = random.randint(5, 7)
        if mission_type == 2:
            priority = random.randint(1, 4)
        missions.append(mission(mission_type=mission_type, priority=priority, location=[x,y]))
    for m in missions:
        m.show_info()