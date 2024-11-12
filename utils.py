import datetime
import pandas as pd
import yfinance as yf


def get_test_data():
    data = pd.read_csv("test.csv", index_col=0)
    data.index = pd.DatetimeIndex(data.index)
    data.columns = data.columns.get_level_values(0)
    # start = data.loc[data['Open'] > 500].index[0]
    # start = pd.Timestamp(start).strftime("%Y-%m-%d")
    start = "2015-06-11"
    end = get_next_month(pd.Timestamp(start).strftime("%Y-%m-%d"))
    monthly = data.loc[start: end]
    return data.loc[end:].iloc[1:], monthly


def get_real_data(sym):
    data = yf.download(sym)
    data.columns = data.columns.get_level_values(0)
    start = data.loc[data['Open'] > 500].index[0]
    start = pd.Timestamp(start).strftime("%Y-%m-%d")
    end = get_next_month(pd.Timestamp(start).strftime("%Y-%m-%d"))

    monthly = data.loc[start: end]
    return data.loc[end:].iloc[1:], monthly


def get_next_month(date_str):
    date_object = datetime.datetime.strptime(date_str, "%Y-%m-%d")
    next_month = date_object + datetime.timedelta(days=31)
    next_month = next_month.replace(day=min(next_month.day, date_object.day))

    next_month_str = next_month.strftime("%Y-%m-%d")

    return next_month_str
