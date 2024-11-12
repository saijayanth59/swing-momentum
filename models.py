import datetime
import pandas as pd
import numpy as np
from math import log10, ceil


class Stock:
    def __init__(self, symbol, data):
        """Initialize the stock with one month's worth of data."""
        self.symbol = symbol
        self.monthly_data = data  # Initialize with the data passed to the object
        self._identity_trend()
        # self.momentum = []

    def update_data(self, new_data):
        """Update the stock's monthly data to slide the window."""
        # Remove the first row and append the new data
        self.monthly_data = pd.concat([self.monthly_data.iloc[1:], new_data])
        # prev_high, prev_low, prev_trend = self.monthly_high, self.monthly_low, self.trend
        self._identity_trend()
        # if prev_trend != self.trend:
        #     self.momentum.append(
        #         [abs(prev_high - self.monthly_high), abs(prev_low - self.monthly_low)])

    def get_average_momentum(self):
        if len(self.momentum) == 0:
            return 0, 0

        return np.mean(np.array(self.momentum))

    def _identity_trend(self):
        # Update high, low, and trend
        self.monthly_high = self.monthly_data['High'].max()
        self.monthly_low = self.monthly_data['Low'].min()
        self.trend = "down" if self.monthly_data['Low'].idxmin(
        ) < self.monthly_data['High'].idxmax() else "up"

    def __str__(self):
        return f"Stock({self.symbol}) -->  Trend: {self.trend}, Monthly High: {self.monthly_high}, Monthly Low: {self.monthly_low}"


class SwingTradingAlgorithm:
    def __init__(self, stock, margin, threshold=5):
        """Initialize the algorithm with the stock and margin."""
        self.stock = stock
        self.margin = margin
        self.orders_history = []  # To track all orders placed
        self.current_order = None  # To track the current open order
        self.trigger = None  # Tracks if a trigger has been met
        self.threshold = threshold
        self.current_day_data = None
        self.hit = 0
        self.miss = 0
        self.trend_miss = 0
        self.can_place = True

    def place_order(self, order_type, quantity, price, stop_loss, target, date=str(datetime.datetime.now())):

        order_params = {
            'order_type': order_type,
            'quantity': quantity,
            'price': price,
            'stop_loss': stop_loss,
            'target': target,
            'date': date,
        }

        self.current_order = Order(**order_params)  # Create a new order object
        self.trigger = None  # Reset the trigger after placing the order
        print(f"Order placed: {self.current_order}")
        self.margin -= price * quantity
        self.can_place = False

    def check_trigger(self):
        """Check for the trigger conditions to place an order."""
        if not self.can_place or self.current_order:
            return
        open_price = self.current_day_data['Open'].iloc[0]
        low_price = self.current_day_data['Low'].iloc[0]
        high_price = self.current_day_data['High'].iloc[0]

        # Check for uptrend trigger (open == low)
        if self.stock.trend == "up" and abs(open_price - low_price) < self.threshold:
            self.trigger = "buy"  # Set trigger to buy when conditions are met
            print(f"Buy trigger found: {self.current_day_data.index[0]}")

        # Check for downtrend trigger (open == high)
        elif self.stock.trend == "down" and abs(open_price - high_price) < self.threshold:
            self.trigger = "sell"  # Set trigger to sell when conditions are met
            print(f"Sell trigger found: {self.current_day_data.index[0]}")

    def place_order_after_trigger(self):
        """Place order on the next day after a trigger is detected."""
        if self.current_order or not self.trigger:
            return
        open_price = self.current_day_data['Open'].iloc[0]
        if self.trigger == "buy":
            self.place_order(
                order_type="buy",
                quantity=self._get_quantities(open_price),
                price=open_price,
                stop_loss=self.stock.monthly_low - self.stock.monthly_low * 0.02,
                target=open_price + open_price * 0.05
            )

        elif self.trigger == "sell":
            self.place_order(
                order_type="sell",
                quantity=self._get_quantities(open_price),
                price=open_price,
                stop_loss=self.stock.monthly_high + self.stock.monthly_high * 0.02,
                target=open_price - open_price * 0.05
            )

    def watch_orders(self):
        """Monitor open orders and check if they hit the target or stop-loss."""
        low_price = self.current_day_data['Low'].iloc[0]
        high_price = self.current_day_data['High'].iloc[0]
        if self.current_order:  # Check if there is an active order

            # Monitor Buy Order
            if self.current_order.order_type == "buy":
                self._buy_trigger(high_price)

            # Monitor Sell Order
            elif self.current_order.order_type == "sell":
                self._sell_trigger(low_price)

        # Check for trend failure
        self._trend_change_trigger()

    def _trend_change_trigger(self):
        curr_trend = self.stock.trend
        self.stock.update_data(self.current_day_data)  # Update the stock data
        if curr_trend != self.stock.trend:  # Check if the trend has changed
            print(f"Trend changed to {self.stock.trend}")
            if self.current_order:
                self._trend_failure()
            self.can_place = True

    def _sell_trigger(self, price):
        if price <= self.current_order.target:
            print("Sell order target hit!", price, self.current_order.target)
            self._success()
            print(f"Updated Margin: {self.margin}")
        elif price >= self.current_order.stop_loss:
            print("Sell order stop-loss hit!",
                  price, self.current_order.target)
            print(f"Updated Margin: {self.margin}")
            self._failure()

    def _buy_trigger(self, price):
        if price >= self.current_order.target:
            print("Buy order target hit!", price, self.current_order.target)
            self._success()
            print(f"Updated Margin: {self.margin}")
        elif price <= self.current_order.stop_loss:
            print("Buy order stop-loss hit!", price, self.current_order.target)
            self._failure()
            print(f"Updated Margin: {self.margin}")

    def _success(self):
        self.hit += 1
        self.current_order.status = 'closed'
        # Pass target value
        self.margin += self.current_order.cancel_order(
            self.current_order.target)
        # Add the order to the history
        self.orders_history.append(self.current_order)
        print(f"Success {self.margin} --> {self.current_order}")
        self.current_order = None

    def _trend_failure(self):
        self.trend_miss += 1
        self.current_order.status = 'closed'
        # Pass target value
        self.margin += self.current_order.cancel_order(
            self.current_day_data['Close'].iloc[0])
        # Add the order to the history
        self.orders_history.append(self.current_order)
        print(f"Trend change failure {self.margin} --> {self.current_order}")
        self.current_order = None

    def _failure(self):
        self.miss += 1
        self.current_order.status = 'closed'
        # Pass stop loss value
        self.margin += self.current_order.cancel_order(
            self.current_order.stop_loss)
        # Add the order to the history
        self.orders_history.append(self.current_order)
        print(f"Failure {self.margin} --> {self.current_order}")
        self.current_order = None

    def _get_quantities(self, price):
        q = (self.margin * 0.80) // price
        digits = ceil(log10(q))
        return round(q, -(digits - 1))

    def get_order_history(self):
        """Return the order history."""
        return self.orders_history


class Order:
    def __init__(self, order_type, quantity, price, stop_loss, target, date):
        """
        Initializes an order with the necessary details.
        :param order_type: Type of order ('Buy' or 'Sell')
        :param quantity: Number of units of the stock
        :param price: Price at which the order was placed
        :param stop_loss: Price at which the order will be stopped
        :param target: Price target for the order
        :param date: Date when the order was placed
        """
        self.order_type = order_type
        self.quantity = quantity
        self.price = price
        self.stop_loss = stop_loss
        self.target = target
        self.date = date
        self.status = 'open'  # Initial status of the order is open
        self.profit = 0.0  # Initial profit is 0
        self.invested = self.price * self.quantity  # Initial investment

    def cancel_order(self, exit_value):
        """
        Cancel the order and calculate profit or loss based on exit value (stop-loss or target).
        :param exit_value: The price at which the order is exited (either stop loss or target)
        :return: Updated invested amount + profit or loss
        """
        # Calculate the difference in price depending on whether it's a Buy or Sell
        gap = exit_value - self.price if self.order_type == 'buy' else self.price - exit_value

        # Calculate profit or loss
        self.profit = gap * self.quantity

        # Return the updated invested amount after adding profit/loss
        return self.invested + self.profit

    def __str__(self):
        """Return a string representation of the order."""
        return (f"Order({self.order_type} {self.quantity} units at {self.price} each) "
                f"Status: {self.status}, Profit: {self.profit}, Invested: {self.invested}, target: {self.target}, stop_loss: {self.stop_loss}")
