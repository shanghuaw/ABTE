import matplotlib.pyplot as plt

task_number = [12, 16, 20, 24, 28, 32, 36, 40, 44, 48,
               52, 56, 60, 64, 68, 72, 76, 80, 84, 88,
               92, 96, 100, 104, 108, 112, 116, 120]
auction_energy = [1.2579*5, 1.2241*5, 1.2312*5, 1.2396*5, 1.2454*5, 1.2581*5, 1.2506*5,
                  1.2509*5, 1.2388*5, 1.2418*5, 1.2358*5, 1.2331*5, 1.2335*5, 1.2375*5,
                  1.2344*5, 1.2276*5, 1.2256*5, 1.2251*5, 1.2204*5, 1.2268*5, 1.2308*5,
                  1.2354*5, 1.2363*5, 1.2341*5, 1.2307*5, 1.2341*5, 1.2322*5, 1.2292*5]
reaction_energy = [2.115*5, 2.0609*5, 2.016*5, 2.134*5, 2.0812*5, 1.9034*5, 1.8931*5,
                   1.9829*5, 1.9884*5, 1.9726*5, 1.8995*5, 1.9051*5, 1.8867*5, 1.9023*5,
                   1.8226*5, 1.801*5, 1.812*5, 1.8461*5, 1.7991*5, 1.9098*5, 1.8652*5,
                   1.8327*5, 1.8319*5, 1.8277*5, 1.881*5, 1.9124*5, 1.8686*5, 1.8205*5]

plt.figure(figsize=(7, 5), dpi=100)
plt.rcParams['font.family']='Times New Roman'
plt.plot(task_number, auction_energy, c='red', label="ABTE")
plt.plot(task_number, reaction_energy, c='blue', label="GEESE")

plt.legend(loc='best')
plt.xticks(range(12, 121, 12))
plt.yticks(range(0, 12, 1))
plt.grid(True, linestyle='--', alpha=0.5)  # 绘制网格
plt.xlabel("Number of Tasks", fontdict={'size': 12})
plt.ylabel("Energy Consumption(%)", fontdict={'size': 12})
plt.show()

# fig, axs = plt.subplots(nrows=1, ncols=3, figsize=(20, 6), dpi=60)
# for i in range(0,1):
#     axs[i].plot(task_number, auction_data[i], c='red', label='ABTE')
#     axs[i].plot(task_number, reaction_data[i], c='blue', label='GEESE')
#     axs[i].set_xlabel("Number of Tasks", fontdict={'size': 12})
#     axs[i].set_ylabel(y_labels[i], fontdict={'size': 12})
#     axs[i].set_title("Comparison of {}".format(titles[i]), fontdict={'size': 14})
#     # 展示散点图
#     axs[i].scatter(task_number, auction_data[i], c='red')
#     axs[i].scatter(task_number, reaction_data[i], c='blue')
#     # 图例位置
#     axs[i].legend(loc='best')
#     # 坐标范围
#     axs[i].set_xticks(range(10, 110, 10))
#     axs[i].set_yticks(range(range_list[i][0], range_list[i][1], range_list[i][2]))
#     # 网格线（alpha表示透明度）
#     axs[i].grid(True, linestyle='--', alpha=0.5)
# # fig.autofmt_xdate()
# plt.show()

# 绘制散点
# plt.scatter(task_number, auction_energy, c='red')
# plt.scatter(task_number, reaction_energy, c='blue')
# 图的标题
# plt.title(title, fontdict={'size': 14})
# 绘制方差errorbar
# plt.errorbar(task_number, auction_energy, yerr=auction_deviation, capsize=1, elinewidth=1, fmt='r')
# plt.errorbar(task_number, reaction_energy, yerr=reaction_deviation, capsize=1, elinewidth=1, fmt='b')