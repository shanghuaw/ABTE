import math
import py_trees as pt
import threading
import py_trees_interface
import custom_behaviours
import time
from algorithm.parameters import params, set_params
import sys

class auction_PyTree(py_trees_interface.PyTree):
    def __init__(self, bt_string, robot_id):
        super().__init__(bt_string, robot_id)

    def tick_auction_bt(self, robot_id):
        """
        Function executing the auction behavior tree
        """
        max_ticks = 200
        ticks = 0
        max_fails = 200
        fails = 0
        requested_successes = 200
        successes = 0
        current_completed_sums = 0
        failed_sums = 0
        while (self.root.status is not pt.common.Status.FAILURE or fails < max_fails) and \
              (self.root.status is not pt.common.Status.SUCCESS or successes < requested_successes) and \
              ticks < max_ticks:
            self.root.tick_once()
            ticks += 1
            if self.root.status is pt.common.Status.SUCCESS:
                successes += 1
            else:
                successes = 0
            if self.root.status is pt.common.Status.FAILURE:
                fails += 1
                if custom_behaviours.chosen_robot == -2:
                    custom_behaviours.task_fails[robot_id] += 1
                    if custom_behaviours.task_fails[robot_id] >= max_fails:
                        print("robot{} task fails:{}".format(robot_id, custom_behaviours.task_fails[robot_id]))
                        break
                    else:
                        continue
            last_completed_sums = current_completed_sums
            while True:
                current_completed_sums = custom_behaviours.task_completes[0] + custom_behaviours.task_completes[1] +\
                               custom_behaviours.task_completes[2]
                if current_completed_sums > last_completed_sums:
                    break
                else:
                    time.sleep(0.5)
            # 分配过的任务数量（包括未能成功分配的）达到规定的上限，或者robot剩余能量在5%-10%之内，则停止该robot的行为
            remain_energy_percent = custom_behaviours.robot_information[robot_id][2] / custom_behaviours.initial_energy[robot_id]
            failed_sums = max(custom_behaviours.task_fails[0], custom_behaviours.task_fails[1], custom_behaviours.task_fails[2])
            if current_completed_sums + failed_sums >= custom_behaviours.max_tasks\
                    or 0.05 <= remain_energy_percent <= 0.1:
                print("robot{} stop tick, remain energy percent:{:.2%}".format(robot_id, remain_energy_percent))
                break
        print("completed tasks:{}, failed tasks:{}".format(
            custom_behaviours.task_completes, custom_behaviours.task_fails))
        print("robot{}: path cost {}, time cost {}".format(
            robot_id, custom_behaviours.total_path_cost[robot_id], custom_behaviours.total_time_cost[robot_id]))
        return ticks


#bt_string = "Sel_TaskDone?_Seq_Sel_HoldCube?_Seq_PlacedCube0?_MoveToCube2_/Seq_Seq_PlacedCube1?_MoveToCube0_/Seq_MoveToCube1_/Sel_PickObject_MoveToPlace_PlaceObject_/Seq_/Sel"
#bt_string = "Sel_TaskDone?_Seq_Sel_Seq_Sel_PlacedCube1?_MoveToCube1_/Sel_Sel_PickObject_PlaceObject_/Sel_PlaceObject_/Seq_Seq_Sel_MoveToPlace_/Sel_PickObject_MoveToCube1_MoveToPlace_MoveToPlace_/Seq_PickObject_PlaceObject_MoveToCube2_/Sel_Sel_Seq_Sel_PickObject_/Sel_/Seq_Seq_Sel_PlacedCube2?_MoveToCube2_MoveToCube1_MoveToCube2_/Sel_Sel_PickObject_/Sel_/Seq_PlacedCube0?_PlaceObject_PlaceObject_MoveToCube0_/Sel_Sel_PickObject_/Sel_Sel_PlacedCube0?_PickObject_/Sel_/Seq_/Sel"
set_params(sys.argv[1:])
bt_string = "Seq_Service_Seq_ReceiveTask_SendInformation_WaitAssign_GEforBTs_/Seq_/Seq"
robot0_tree = auction_PyTree(bt_string, 0)
robot1_tree = auction_PyTree(bt_string, 1)
robot2_tree = auction_PyTree(bt_string, 2)
robot0_thread = threading.Thread(target=robot0_tree.tick_auction_bt, args=(0, ))
robot1_thread = threading.Thread(target=robot1_tree.tick_auction_bt, args=(1, ))
robot2_thread = threading.Thread(target=robot2_tree.tick_auction_bt, args=(2, ))
robot0_thread.start()
robot1_thread.start()
robot2_thread.start()