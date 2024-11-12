import pandas as pd
from utils import get_test_data
from models import *

data, monthly = get_test_data()
stock = Stock("CIPLA", monthly)
algo = SwingTradingAlgorithm(stock, 1000000)

for i in range(data.shape[0]):
    # print(stock.monthly_data)s
    curr = data.iloc[i:i + 1]
    algo.current_day_data = curr

    algo.place_order_after_trigger()
    algo.watch_orders()
    algo.check_trigger()
    # print(stock)
    # print(algo.current_order)

print(algo.margin, algo.hit, algo.miss, algo.trend_miss)
