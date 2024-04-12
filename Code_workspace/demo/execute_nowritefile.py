import sys
import threading
import statistics
import py_interface
import mission_behaviors
from mission_behaviors import robot_info
from mission import mission_list
from time import sleep

args = sys.argv
robot_nums = int(args[1])
mission_nums = int(args[2])
print("input robot numbers:", robot_nums)
print("input mission numbers:", mission_nums)
bt_string = "Seq_CheckState_GetNeighborMission_Sel_MoveToMission_Seq_IsBlocked?_AvoidObstacle_/Seq_/Sel_ReachTarget?_ExecuteMission_/Seq"
robot_tree = list()
robot_thread = list()
for i in range(0, robot_nums):
    robot_tree.append(py_interface.PyTree(bt_string, i, mission_nums))
for i in range(0, robot_nums):
    robot_thread.append(threading.Thread(target=robot_tree[i].tick_bt))
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
    energy_cost = mission_behaviors.INITIAL_ENERGY - robot_info['attribute'][i][1]
    energy_cost_array.append(energy_cost / mission_behaviors.INITIAL_ENERGY)
    print("robot{}:\npath cost:{}\ntime cost:{}\nenergy cost:{}\nremain energy:{}, {:.2%}\n"
          "accomplished missions:{}\naccomplished prior missions:{}\ntimeout missions:{}".format(i,
            robot_info['total_path_cost'][0], robot_info['total_time_cost'][0],
            energy_cost, robot_info['attribute'][0][1], robot_info['attribute'][i][1] / mission_behaviors.INITIAL_ENERGY,
            robot_info['accomplished_missions'][0], robot_info['prior_missions'][i], robot_info['timeout_missions'][0]))
    sum_path_cost += robot_info['total_path_cost'][i]
    # max_time_cost = max(robot_info['total_time_cost'][i], max_time_cost)
    sum_time_cost += robot_info['total_time_cost'][i]
    sum_score += robot_info['score'][i]
    sum_accomplished_missions += len(robot_info['accomplished_missions'][i])
    accomplished_prior_missions += len(robot_info['prior_missions'][i])
    sum_timeout_missions += len(robot_info['timeout_missions'][i])
    sum_energy_remain += robot_info['attribute'][i][1]
energy_cost_mean_value = 1 - sum_energy_remain / (mission_behaviors.INITIAL_ENERGY * robot_nums)
energy_cost_std_deviation = statistics.stdev(energy_cost_array)
energy_cost_per_mission = (mission_behaviors.INITIAL_ENERGY * robot_nums - sum_energy_remain) / mission_nums
print("sum:\npath cost:{}\ntime cost:{}"
      "\nenergy cost mean value:{:.2%}\nenergy cost std deviation:{}\nenergy cost per mission:{}"
      "\naccomplished missions:{}\naccomplished prior missions:{}\ntimeout missions:{}"
      "\naccomplished prior missions ratio:{}".format(
    sum_path_cost, sum_time_cost,
    energy_cost_mean_value, energy_cost_std_deviation, energy_cost_per_mission,
    sum_accomplished_missions, accomplished_prior_missions,sum_timeout_missions,
    accomplished_prior_missions / total_prior_missions))