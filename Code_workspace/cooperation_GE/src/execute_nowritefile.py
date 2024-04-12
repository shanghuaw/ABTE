import sys
import threading
import statistics
import py_trees_interface
import robot
from time import sleep
from mission import mission_list
from robot import robot_list

args = sys.argv
robot_nums = int(args[1])
mission_nums = int(args[2])
print("input robot numbers:", robot_nums)
print("input mission numbers:", mission_nums)
bt_string = "Seq_Service_ReceiveNotification_SendInformation_WaitAllocation_GEForBTs_/Seq"
robot_tree = list()
robot_thread = list()
for i in range(0, robot_nums):
    robot_tree.append(py_trees_interface.PyTree(bt_string, i, robot_nums, mission_nums))
for i in range(0, robot_nums):
    robot_thread.append(threading.Thread(target=robot_tree[i].tick_bt, args=(1, )))
for i in range(0, robot_nums):
    robot_thread[i].start()

sleep(5)
total_prior_missions = 0
for m in mission_list[mission_nums]:
    if m.type != 3:
        total_prior_missions += 1
sum_path_cost = 0
sum_time_cost = 0
max_time_cost = 0
sum_score = 0
sum_accomplished_missions = 0
accomplished_prior_missions = 0
sum_timeout_missions = 0
sum_energy_remain = 0
energy_cost_array = list()
for i in range(0, robot_nums):
    energy_cost = robot.INITIAL_ENERGY - robot_list[i].robot_information[2]
    energy_cost_array.append(energy_cost / robot.INITIAL_ENERGY)
    print("robot{}:\npath cost:{}\ntime cost:{}\nenergy cost:{}\nremain energy:{}, {:.2%}\n"
          "accomplished missions:{}\naccomplished prior missions:{}\ntimeout missions:{}".format(i,
            robot_list[i].total_path_cost, robot_list[i].total_time_cost, energy_cost,
            robot_list[i].robot_information[2], robot_list[i].robot_information[2] / robot.INITIAL_ENERGY,
            robot_list[i].accomplished_missions, robot_list[i].prior_missions, robot_list[i].timeout_missions))
    sum_path_cost += robot_list[i].total_path_cost
    # max_time_cost = max(robot_list[i].total_time_cost, max_time_cost)
    sum_time_cost += robot_list[i].total_time_cost
    sum_score += robot_list[i].total_score
    sum_accomplished_missions += len(robot_list[i].accomplished_missions)
    accomplished_prior_missions += len(robot_list[i].prior_missions)
    sum_timeout_missions += len(robot_list[i].timeout_missions)
    sum_energy_remain += robot_list[i].robot_information[2]
energy_cost_mean_value = 1 - sum_energy_remain / (robot.INITIAL_ENERGY * robot_nums)
energy_cost_std_deviation = statistics.stdev(energy_cost_array)
energy_cost_per_mission = (robot.INITIAL_ENERGY * robot_nums - sum_energy_remain) / mission_nums
print("sum:\npath cost:{}\ntime cost:{}"
      "\nenergy cost mean value:{:.2%}\nenergy cost std deviation:{}\nenergy cost per mission:{}"
      "\naccomplished missions:{}\naccomplished prior missions:{}\ntimeout missions:{}"
      "\naccomplished prior missions ratio:{}".format(
    sum_path_cost, sum_time_cost,
    energy_cost_mean_value, energy_cost_std_deviation, energy_cost_per_mission,
    sum_accomplished_missions, accomplished_prior_missions, sum_timeout_missions,
    accomplished_prior_missions / total_prior_missions))