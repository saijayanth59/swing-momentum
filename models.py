class Stock:
    def __init__(self, symbol, data):
        """Initialize the stock with one month's worth of data."""
        self.symbol = symbol
        self.monthly_data = data  # Initialize with the data passed to the object
        self.monthly_high = self.monthly_data['High'].max()
        self.monthly_low = self.monthly_data['Low'].min()
        self.trend = "up" if self.monthly_data['Low'].idxmin() < self.monthly_data['High'].idxmax() else "down"
    
    def update_data(self, new_data):
        """Update the stock's monthly data to slide the window."""
        # Remove the first row and append the new data
        self.monthly_data = self.monthly_data.iloc[1:].append(new_data)
        
        # Update high, low, and trend
        self.monthly_high = self.monthly_data['High'].max()
        self.monthly_low = self.monthly_data['Low'].min()
        self.trend = "up" if self.monthly_data['Low'].idxmin() < self.monthly_data['High'].idxmax() else "down"


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
    
    def place_order(self, order_type, quantity, price, stop_loss, target, date=str(datetime.datetime.now())):
        """Place an order and record it in the order history."""
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
    
    def check_trigger(self):
        """Check for the trigger conditions to place an order."""
        open_price = self.current_day_data['Open']
        low_price = self.current_day_data['Low']
        high_price = self.current_day_data['High']

        # Check for uptrend trigger (open == low)
        if self.stock.trend == "up" and abs(open_price - low_price) < self.threshold:
            self.trigger = "buy"  # Set trigger to buy when conditions are met
            print(f"Buy trigger found: {self.current_day_data}")
        
        # Check for downtrend trigger (open == high)
        elif self.stock.trend == "down" and abs(open_price - high_price) < self.threshold:
            self.trigger = "sell"  # Set trigger to sell when conditions are met
            print(f"Sell trigger found: {self.current_day_data}")
    
    def place_order_after_trigger(self):
        """Place order on the next day after a trigger is detected."""
        if self.trigger == "buy":
            open_price = self.current_day_data['Open']
            self.place_order(
                order_type="buy", 
                quantity=100, 
                price=open_price, 
                stop_loss=self.stock.monthly_low, 
                target=self.stock.monthly_high
            )
        
        elif self.trigger == "sell":
            open_price = self.current_day_data['Open']
            self.place_order(
                order_type="sell", 
                quantity=100, 
                price=open_price, 
                stop_loss=self.stock.monthly_high, 
                target=self.stock.monthly_low
            )
    

    def watch_orders(self):
        """Monitor open orders and check if they hit the target or stop-loss."""

        if self.current_order:  # Check if there is an active order
            price = self.current_day_data['Close']
            
            # Monitor Buy Order
            if self.current_order.order_type == "Buy":
                self._buy_trigger(price)
            
            # Monitor Sell Order
            elif self.current_order.order_type == "Sell":
                self._sell_trigger(price)
            
            # Print the updated margin after order is closed
            print(f"Updated Margin: {self.margin}")
        
        self._trend_failure_trigger(self.current_day_data)  # Check for trend failure
    
    
    def _trend_failure_trigger(self):
        curr_trend = self.stock.trend
        self.stock.update_data(self.current_day_data)  # Update the stock data
        if curr_trend != self.stock.trend:  # Check if the trend has changed
            print(f"Trend changed to {self.stock.trend}")
            if self.current_order:
                self._failure()

    def _sell_trigger(self, price):
        if price <= self.current_order.target:
            print("Sell order target hit!")
            self._success()
        elif price >= self.current_order.stop_loss:
            print("Sell order stop-loss hit!")
            self._failure()

    def _buy_trigger(self, price):
        if price >= self.current_order.target:
            print("Buy order target hit!")
            self._success()
        elif price <= self.current_order.stop_loss:
            print("Buy order stop-loss hit!")
            self._failure()

    def _success(self):
        self.current_order.status = 'closed'
        self.margin += self.current_order.cancel_order(self.current_order.target)  # Pass target value
        self.orders_history.append(self.current_order)  # Add the order to the history
        self.current_order = None
    
    def _failure(self):
        self.current_order.status = 'closed'
        self.margin += self.current_order.cancel_order(self.current_order.stop_loss)  # Pass stop loss value
        self.orders_history.append(self.current_order)  # Add the order to the history
        self.current_order = None

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
        gap = exit_value - self.price if self.order_type == 'Buy' else self.price - exit_value

        # Calculate profit or loss
        self.profit = gap * self.quantity

        # Return the updated invested amount after adding profit/loss
        return self.invested + self.profit

    def __str__(self):
        """Return a string representation of the order."""
        return (f"Order({self.order_type} {self.quantity} units at {self.price} each) "
                f"Status: {self.status}, Profit: {self.profit}, Invested: {self.invested}")

