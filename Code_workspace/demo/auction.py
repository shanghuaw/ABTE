import copy

# 报价函数
def bidding():
    new_bid = {}
    for bidder in bidder_set:
        if bidder in current_assignment:
            continue
        else:
            values = []
            bidder_objects = copy.deepcopy(available_objects_list[bidder])
            for obj in bidder_objects:
                values.append(value_for_bidders[bidder, obj] - current_price[obj])
            max_value = max(values)  # 最大收益
            bid_target = bidder_objects[values.index(max_value)]  # 最大收益对象，即竞拍对象
            values.remove(max_value)
            submax_value = max(values)  # 次大收益
            # 计算报价时用竞拍物品的原价值而不是减去价格后的价值，可以确保报价一定比之前的报价高
            bid_price = value_for_bidders[bidder, bid_target] - submax_value + epsilon
            if bid_target in new_bid:
                new_bid[bid_target][0].append(bidder)
                new_bid[bid_target][1].append(bid_price)
            else:
                new_bid[bid_target] = [[bidder], [bid_price]]
    return new_bid


# 分配函数
def assigning(bid_prices):
    for obj in object_set:
        if obj in bid_prices:
            bidders, prices = bid_prices[obj]
            max_price = max(prices)  # 所有竞拍者中的最高报价
            max_bidder = bidders[prices.index(max_price)]
            current_price[obj] = max_price  # 刷新物品价格
            # 将有新报价的物品与出价最高的竞拍者的组合插入current_assignment
            # 如果物品上一轮有报价，则进行替换，确保物品与竞拍者一一对应
            for bidder in current_assignment:
                if current_assignment[bidder] == obj:
                    current_assignment.pop(bidder)
                    current_assignment[max_bidder] = obj
                    break
            if max_bidder not in current_assignment:
                current_assignment[max_bidder] = obj


if __name__ == '__main__':
    bidder_set = ['R1', 'R2', 'R3', 'R4', 'R5', 'R6']
    object_set = ['T1', 'T2', 'T3', 'T4', 'T5', 'T6']
    available_objects_list = {
        'R1': ['T1', 'T2', 'T3', 'T4', 'T5', 'T6'],
        'R2': ['T1', 'T2', 'T3', 'T4', 'T5', 'T6'],
        'R3': ['T1', 'T2', 'T3', 'T4', 'T5', 'T6'],
        'R4': ['T1', 'T2', 'T3', 'T4', 'T5', 'T6'],
        'R5': ['T1', 'T2', 'T3', 'T4', 'T5', 'T6'],
        'R6': ['T1', 'T2', 'T3', 'T4', 'T5', 'T6']
    }
    value_for_bidders = {
        ('R1', 'T1'): 11, ('R1', 'T2'): 18, ('R1', 'T3'): 11, ('R1', 'T4'): 18, ('R1', 'T5'): 33, ('R1', 'T6'): 4,
        ('R2', 'T1'): 4, ('R2', 'T2'): 34, ('R2', 'T3'): 33, ('R2', 'T4'): 32, ('R2', 'T5'): 26, ('R2', 'T6'): 23,
        ('R3', 'T1'): 3, ('R3', 'T2'): 0, ('R3', 'T3'): 27, ('R3', 'T4'): 24, ('R3', 'T5'): 14, ('R3', 'T6'): 9,
        ('R4', 'T1'): 25, ('R4', 'T2'): 15, ('R4', 'T3'): 25, ('R4', 'T4'): 23, ('R4', 'T5'): 7, ('R4', 'T6'): 26,
        ('R5', 'T1'): 30, ('R5', 'T2'): 18, ('R5', 'T3'): 34, ('R5', 'T4'): 20, ('R5', 'T5'): 17, ('R5', 'T6'): 29,
        ('R6', 'T1'): 5, ('R6', 'T2'): 35, ('R6', 'T3'): 34, ('R6', 'T4'): 4, ('R6', 'T5'): 17, ('R6', 'T6'): 28
    }
    current_assignment = {'R1': 'T5', 'R2': 'T2', 'R3': 'T3', 'R4': 'T6'}
    current_price = {'T1': 0, 'T2': 0, 'T3': 0, 'T4': 0, 'T5': 0, 'T6': 0}
    epsilon = 0.1
    k = 1
    while True:
        new_bid = bidding()
        if len(new_bid) > 0:
            assigning(new_bid)
        else:
            break
        k += 1
        print("第{}次竞拍：".format(k))
        print("\t新报价为：")
        print("\t", new_bid)
        print("\t竞拍结果为：")
        print("\t", current_assignment)
        print("\t最新定价为：")
        print("\t", current_price)