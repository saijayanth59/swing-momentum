import pandas as pd
import datetime
from main import *
import yfinance as yf


def pre_process(data):
    data.index = data.index.astype(str)
    start = data.loc[data['Open'] > 500].index[0]
    end = get_next_month(start)
    monthly = data.loc[start: end]
    high_idx, low_idx = monthly['High'].argmax(), monthly['Low'].argmin()
    trend = "up" if high_idx < low_idx else 'down'
    return data.iloc[monthly.shape[0]:], monthly.iloc[high_idx], monthly.iloc[low_idx], trend


def get_next_month(date_str):
    date_object = datetime.datetime.strptime(date_str, "%Y-%m-%d")
    next_month = date_object + datetime.timedelta(days=31)
    next_month = next_month.replace(day=min(next_month.day, date_object.day))

    next_month_str = next_month.strftime("%Y-%m-%d")

    return next_month_str


if __name__ == '__main__':
    data = yf.download("CIPLA.NS")
    data, high, low, trend = pre_process(data.loc['2018-02-01':])
    swing = Swing(day_low=low, day_high=high, trend=trend, margin=1000000.0)
    Qty = 500
    target_threshold = 100
    stoploss_threshold = 0
    for i in range(data.shape[0]):
        curr_day = data.iloc[i]
        # can place order
        swing.place_order(curr_day, Qty=Qty, stoploss_threshold=stoploss_threshold,
                          target_threshold=target_threshold)

        # check trend update
        swing.update_trend(curr_day)
        # check indicator
        swing.check_indicator(curr_day)
        # watch holdings
        swing.watch_holdings(curr_day)

        # print(swing.margin)
    if swing.order:
        print(swing.order.invested + swing.margin)
    print(swing.margin, len(swing.orders_history))
