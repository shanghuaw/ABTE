import matplotlib.pyplot as plt

task_number = [12, 16, 20, 24, 28, 32, 36, 40, 44, 48,
               52, 56, 60, 64, 68, 72, 76, 80, 84, 88,
               92, 96, 100, 104, 108, 112, 116, 120]
robot_number = [4, 8, 12, 16, 20, 24, 28,
                32, 36, 40, 44, 48, 52, 56, 60]
auction_coverage1 = [1.0*100, 1.0*100, 1.0*100, 1.0*100, 1.0*100, 1.0*100, 1.0*100,
                     1.0*100, 1.0*100, 1.0*100, 1.0*100, 1.0*100, 1.0*100, 0.9375*100,
                     0.8824*100, 0.8333*100, 0.7895*100, 0.75*100, 0.7143*100, 0.6818*100, 0.6522*100,
                     0.625*100, 0.6*100, 0.5769*100, 0.5556*100, 0.5357*100, 0.5172*100, 0.5*100]
reaction_coverage1 = [1.0*100, 1.0*100, 1.0*100, 1.0*100, 1.0*100, 0.9583*100, 0.963*100,
                      0.8333*100, 0.7879*100, 0.7222*100, 0.641*100, 0.6429*100, 0.5333*100, 0.5*100,
                      0.5294*100, 0.5*100, 0.4035*100, 0.3667*100, 0.3968*100, 0.3485*100, 0.3333*100,
                      0.3333*100, 0.3067*100, 0.2949*100, 0.284*100, 0.2619*100, 0.2529*100, 0.2444*100]
auction_coverage2 = [16.67, 33.33, 50.0, 66.67, 83.33, 97.78, 100.0,
                     100.0, 100.0, 100.0, 100.0, 100.0, 100.0, 100.0, 100.0]
reaction_coverage2 = [6.67, 15.56, 26.67, 35.56, 46.67, 54.44, 65.56,
                      73.33, 78.89, 90.0, 94.44, 100.0, 100.0, 100.0, 100.0]
# increase tasks
plt.figure(figsize=(7, 5), dpi=100)
plt.rcParams['font.family']='Times New Roman'
plt.plot(task_number, auction_coverage1, c='red', label="ABTE")
plt.plot(task_number, reaction_coverage1, c='blue', label="GEESE")
plt.legend(loc='best')
plt.xticks(range(12, 121, 12))
plt.yticks(range(0, 101, 10))
plt.grid(True, linestyle='--', alpha=0.5)
plt.xlabel("Number of Agents", fontdict={'size': 12})
plt.ylabel("Coverage Ratio(%)", fontdict={'size': 12})
plt.show()
# increase robots
plt.figure(figsize=(7, 5), dpi=100)
plt.rcParams['font.family']='Times New Roman'
plt.plot(robot_number, auction_coverage2, c='red', label="ABTE")
plt.plot(robot_number, reaction_coverage2, c='blue', label="GEESE")
plt.legend(loc='best')
plt.xticks(range(4, 61, 4))
plt.yticks(range(0, 101, 10))
plt.grid(True, linestyle='--', alpha=0.5)
plt.xlabel("Number of Agents", fontdict={'size': 12})
plt.ylabel("Coverage Ratio(%)", fontdict={'size': 12})
plt.show()