import matplotlib.pyplot as plt

task_number = [12, 16, 20, 24, 28, 32, 36, 40, 44, 48,
               52, 56, 60, 64, 68, 72, 76, 80, 84, 88,
               92, 96, 100, 104, 108, 112, 116, 120]
auction_energy = [0.0629*100, 0.0816*100, 0.1026*100, 0.124*100, 0.1453*100, 0.1677*100, 0.1876*100,
                  0.2085*100, 0.2271*100, 0.2484*100, 0.2678*100, 0.2877*100, 0.3084*100, 0.33*100,
                  0.3498*100, 0.3683*100, 0.3881*100, 0.4084*100, 0.4271*100, 0.4498*100, 0.4718*100,
                  0.4942*100, 0.5151*100, 0.5348*100, 0.5538*100, 0.5759*100, 0.5956*100, 0.6146*100]
reaction_energy = [0.1058*100, 0.1374*100, 0.168*100, 0.2134*100, 0.2428*100, 0.2538*100, 0.284*100,
                   0.3305*100, 0.3645*100, 0.3945*100, 0.4116*100, 0.4445*100, 0.4717*100, 0.5073*100,
                   0.5164*100, 0.5403*100, 0.5738*100, 0.6154*100, 0.6297*100, 0.7003*100, 0.715*100,
                   0.7331*100, 0.7633*100, 0.792*100, 0.8464*100, 0.8925*100, 0.9032*100, 0.9103*100]
auction_deviation = [0.0377*100, 0.0375*100, 0.0288*100, 0.0342*100, 0.0352*100, 0.0246*100, 0.0128*100,
                     0.0255*100, 0.027*100, 0.0371*100, 0.0248*100, 0.0253*100, 0.0186*100, 0.0273*100,
                     0.0375*100, 0.0356*100, 0.0337*100, 0.0297*100, 0.034*100, 0.0335*100, 0.028*100,
                     0.0185*100, 0.0356*100, 0.0293*100, 0.0388*100, 0.0318*100, 0.0304*100, 0.0343*100]
reaction_deviation = [0.0198*100, 0.0442*100, 0.0465*100, 0.0193*100, 0.0402*100, 0.044*100, 0.0408*100,
                      0.0427*100, 0.0389*100, 0.0446*100, 0.0487*100, 0.0415*100, 0.0382*100, 0.0439*100,
                      0.0293*100, 0.0328*100, 0.0419*100, 0.038*100, 0.0374*100, 0.0355*100, 0.0387*100,
                      0.0432*100, 0.0317*100, 0.0291*100, 0.0339*100, 0.0347*100, 0.0318*100, 0.0202*100]

plt.figure(figsize=(7, 5), dpi=100)
plt.rcParams['font.family']='Times New Roman'
plt.plot(task_number, auction_energy, c='red', label="ABTE")
plt.plot(task_number, reaction_energy, c='blue', label="GEESE")

# 绘制带方差的折线图
r1 = list(map(lambda x: x[0] - x[1], zip(auction_energy, auction_deviation)))  # 上方差
r2 = list(map(lambda x: x[0] + x[1], zip(auction_energy, auction_deviation)))  # 下方差
r3 = list(map(lambda x: x[0] - x[1], zip(reaction_energy, reaction_deviation)))  # 上方差
r4 = list(map(lambda x: x[0] + x[1], zip(reaction_energy, reaction_deviation)))  # 下方差
plt.fill_between(task_number, r1, r2, color='red', alpha=0.1)
plt.fill_between(task_number, r3, r4, color='blue', alpha=0.1)

plt.legend(loc='best')
plt.xticks(range(12, 121, 12))
plt.yticks(range(0, 100, 10))
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