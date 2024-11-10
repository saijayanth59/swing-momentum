import pandas as pd
import datetime
import yfinance as yf

data = yf.download("CIPLA.NS")

print(data)
