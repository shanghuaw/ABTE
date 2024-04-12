import matplotlib.pyplot as plt

fig, axs = plt.subplots(nrows=1, ncols=3, figsize=(20, 6), dpi=100)
task_number = [10, 20, 30, 40, 50]
auction_time = [210.3, 403.35, 598.62, 830.48, 1003.88]
reaction_time = [212.25, 436.14, 654.24, 902.54, 1145.87]
auction_path = [642, 1356, 2143, 2387, 3261]
reaction_path = [429, 815, 1166, 1421, 2048]
auction_score = [273.62, 563.57, 934.39, 1024.35, 1116.65]
reaction_score =[140.25, 280.5, 390.55, 498.24, 600.2]
auction_data = [auction_time, auction_path, auction_score]
reaction_data = [reaction_time, reaction_path, reaction_score]
range_list = [[1300, 100], [3600, 200], [1300, 100]]
y_labels = ["Time Cost", "Path Cost", "Score"]
for i in range(3):
    axs[i].plot(task_number, auction_data[i], c='red', label='Auction')
    axs[i].plot(task_number, reaction_data[i], c='blue', label='Reaction')
    axs[i].set_xlabel("Numbers of task", fontdict={'size': 12})
    axs[i].set_ylabel(y_labels[i], fontdict={'size': 12})
    axs[i].set_title("Comparison of {}".format(y_labels[i]), fontdict={'size': 16})
    # 展示散点图
    axs[i].scatter(task_number, auction_data[i], c='red')
    axs[i].scatter(task_number, reaction_data[i], c='blue')
    # 图例位置
    axs[i].legend(loc='best')
    # 坐标范围
    axs[i].set_xticks(range(10, 60, 10))
    axs[i].set_yticks(range(0, range_list[i][0], range_list[i][1]))
    # 网格线（alpha表示透明度）
    axs[i].grid(True, linestyle='--', alpha=0.5)
# fig.autofmt_xdate()
plt.show()