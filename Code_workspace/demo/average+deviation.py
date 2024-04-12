import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np

auction_energy = [7.56*150, 15.33*150, 23.95*150, 31.29*150, 39.96*150, 46.89*150, 55.06*150, 63.04*150, 71.83*150, 79.47*150]
reaction_energy = [10.24*150, 19.93*150, 26.71*150, 34.85*150, 42.29*150, 50.46*150, 59.59*150, 68.36*150, 77.86*150, 88.51*150]
# auction_energy = [7.56*30, 15.33*30, 23.95*30, 31.29*30, 39.96*30, 46.89*30, 55.06*30, 63.04*30, 71.83*30, 79.47*30]
# reaction_energy = [10.24*30, 19.93*30, 26.71*30, 34.85*30, 42.29*30, 50.46*30, 59.59*30, 68.36*30, 77.86*30, 88.51*30]
auction_tasks = [20, 19, 15, 16, 18, 17]
reaction_tasks = [12, 10, 12, 13, 11, 11, 10, 6]

# def cal_average(x):
#     ave_sum = 0
#     for idx in range(1, len(x)):
#         ave_sum += x[idx] - x[idx-1]
#     return ave_sum / (len(x) - 1)
#
# def cal_standard_deviation(x):
#     value = cal_average(x)
#     square_sum = 0
#     for idx in range(1, len(x)):
#         square_sum += (x[idx] - x[idx-1] - value) ** 2
#     return (square_sum / (len(x) - 1)) ** 0.5

def cal_average(x):
    ave_sum = 0
    for idx in range(0, len(x)):
        ave_sum += x[idx]
    return ave_sum / len(x)

def cal_standard_deviation(x):
    value = cal_average(x)
    square_sum = 0
    for idx in range(0, len(x)):
        square_sum += (x[idx] - value) ** 2
    return (square_sum / len(x)) ** 0.5

# mpl.rcParams["font.sans-serif"]=["Times New Roman"]
mpl.rcParams["axes.unicode_minus"]=False
# some simple data
x = np.arange(2)
average_value = [cal_average(auction_tasks), cal_average(reaction_tasks)]
standard_deviation = [cal_standard_deviation(auction_tasks), cal_standard_deviation(reaction_tasks)]
y1 = [average_value[0], standard_deviation[0]]
y2 = [average_value[1], standard_deviation[1]]
bar_width = 0.35
tick_label=["Mean Value", "Standard Deviation"]
# create bar
plt.bar(x, y1, bar_width, color="c", align="center", label="GEABT", alpha=0.5)
plt.bar(x+bar_width, y2, bar_width, color="b", align="center", label="GEESE", alpha=0.5)
for a,b in zip(x,y1):   #柱子上的数字显示
    plt.text(a,b,'%.2f'%b,ha='center',va='bottom',fontsize=8)
for a,b in zip(x+bar_width,y2):
    plt.text(a,b,'%.2f'%b,ha='center',va='bottom',fontsize=8)
# plt.xlabel("测试难度")
plt.ylabel("Energy(kJ)", fontdict={'size': 12})
plt.xticks(x+bar_width/2,tick_label)
plt.title("Assessment of Energy Overhead", fontdict={'size': 14})
plt.legend()
plt.show()