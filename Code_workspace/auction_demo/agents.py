import threading
import py_trees_interface
from time import sleep
import custom_behaviours
import sys

bt_string = "Seq_Service_ReceiveNotification_SendInformation_WaitAllocation_GEForBTs_/Seq"
robot0_tree = py_trees_interface.PyTree(bt_string, 0)
robot1_tree = py_trees_interface.PyTree(bt_string, 1)
robot2_tree = py_trees_interface.PyTree(bt_string, 2)
robot0_thread = threading.Thread(target=robot0_tree.tick_bt, args=(1, ))
robot1_thread = threading.Thread(target=robot1_tree.tick_bt, args=(1, ))
robot2_thread = threading.Thread(target=robot2_tree.tick_bt, args=(1, ))
robot0_thread.start()
robot1_thread.start()
robot2_thread.start()

sleep(25)
print("robot0:\npath cost:{}\ntime cost:{}\nenergy cost:{}\nscore:{}\naccomplished missions:{}".format(
    custom_behaviours.total_path_cost[0], custom_behaviours.total_time_cost[0],
    custom_behaviours.INITIAL_ENERGY-custom_behaviours.robot_information[0][2],
    custom_behaviours.total_score[0], custom_behaviours.accomplished_missions[0]))
print("robot1:\npath cost:{}\ntime cost:{}\nenergy cost:{}\nscore:{}\naccomplished missions:{}".format(
    custom_behaviours.total_path_cost[1], custom_behaviours.total_time_cost[1],
    custom_behaviours.INITIAL_ENERGY-custom_behaviours.robot_information[1][2],
    custom_behaviours.total_score[1], custom_behaviours.accomplished_missions[1]))
print("robot2:\npath cost:{}\ntime cost:{}\nenergy cost:{}\nscore:{}\naccomplished missions:{}".format(
    custom_behaviours.total_path_cost[2], custom_behaviours.total_time_cost[2],
    custom_behaviours.INITIAL_ENERGY-custom_behaviours.robot_information[2][2],
    custom_behaviours.total_score[2], custom_behaviours.accomplished_missions[2]))
sum_path_cost = 0
max_time_cost = 0
sum_score = 0
sum_accomplished_missions = 0
for i in range(0 ,3):
    sum_path_cost += custom_behaviours.total_path_cost[i]
    max_time_cost = max(custom_behaviours.total_time_cost[i], max_time_cost)
    sum_score += custom_behaviours.total_score[i]
    sum_accomplished_missions += len(custom_behaviours.accomplished_missions[i])
print("sum:\npath cost:{}\ntime cost:{}\nscore:{}\naccomplished missions:{}".format(
    sum_path_cost, max_time_cost, sum_score, sum_accomplished_missions))
energy0 = custom_behaviours.robot_information[0][2] / custom_behaviours.INITIAL_ENERGY
energy1 = custom_behaviours.robot_information[1][2] / custom_behaviours.INITIAL_ENERGY
energy2 = custom_behaviours.robot_information[2][2] / custom_behaviours.INITIAL_ENERGY
print("remain energy:\nrobot0:{}, {:.2%}\nrobot1:{}, {:.2%}\nrobot2:{}, {:.2%}".format(
    custom_behaviours.robot_information[0][2], energy0, custom_behaviours.robot_information[1][2], energy1,
    custom_behaviours.robot_information[2][2], energy2))