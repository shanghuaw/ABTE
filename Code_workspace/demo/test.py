import random
from mission import mission_list

obstacle_range = [[15, 20, 10, 25], [50, 62, 60 ,75], [40, 58, 42, 48]]

def in_range(location, ranges):
    for i in range(0, len(ranges)):
        if location[0] in range(ranges[i][0], ranges[i][1] + 1)\
                and location[1] in range(ranges[i][2], ranges[i][3] + 1):
            return i
    return -1

def generate_mission(number):
    missions = list()
    locations = list()
    for m in mission_list:
        locations.append(m.location)
    zero_nums = 0
    one_nums = 0
    two_nums = 0
    for i in range(0, number):
        mission_type = 0
        if zero_nums / number < 0.2 and one_nums / number < 0.3 and two_nums / number < 0.5:
            mission_type = random.randint(0, 2)
        elif zero_nums / number >= 0.2 and one_nums / number < 0.3 and two_nums / number < 0.5:
            mission_type = random.randint(1, 2)
        elif zero_nums / number >= 0.2 and one_nums / number >= 0.3 and two_nums / number < 0.5:
            mission_type = 2
        elif zero_nums / number < 0.2 and one_nums / number >= 0.3 and two_nums / number < 0.5:
            x = [0, 2]
            mission_type = random.choice(x)
        elif zero_nums / number < 0.2 and one_nums / number >= 0.3 and two_nums / number >= 0.5:
            mission_type = 0
        elif zero_nums / number < 0.2 and one_nums / number < 0.3 and two_nums / number >= 0.5:
            mission_type = random.randint(0, 1)
        elif zero_nums / number >= 0.2 and one_nums / number < 0.3 and two_nums / number >= 0.5:
            mission_type = 1
        priority = 0
        if mission_type == 0:
            priority = random.randint(8, 10)
            zero_nums += 1
        if mission_type == 1:
            priority = random.randint(5, 7)
            one_nums += 1
        if mission_type == 2:
            priority = random.randint(1, 4)
            two_nums += 1
        x = random.randint(0, 100)
        y = random.randint(0, 100)
        while not in_range([x, y], obstacle_range) == -1 or [x, y] in locations:
            x = random.randint(0, 100)
            y = random.randint(0, 100)
        locations.append([x, y])
        missions.append("mission({}, {}, {})".format(mission_type, priority, [x, y]))
    print(missions)
    
generate_mission(10)