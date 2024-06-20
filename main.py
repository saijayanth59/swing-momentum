class Order:
    def __init__(self, price, type, Qty, stoploss, target, place_date=None, close_date=None):
        self.price = price
        self.type = type
        self.Qty = Qty
        self.stoploss = stoploss
        self.target = target
        self.place = place_date
        self.close = close_date
        self.invested = self.price * self.Qty
        # self.status = False
        self.indicator_day = None
        self.profit = 0

    def cancel_order(self, end_price):
        gap = end_price - self.price if self.type == 'Buy' else self.price - end_price
        self.profit = gap * self.Qty
        return self.invested + self.profit


class Swing:
    def __init__(self, day_low, day_high, trend, margin):
        self.day_low = day_low  # series
        self.day_high = day_high  # series

        self.margin = margin  # double

        self.trend = trend  # string up or down
        self.order = None  # object
        self.indicator = None  # series

        self.indicators_history = []
        self.orders_history = []
        self.highs_history = [day_high['High']]
        self.lows_history = [day_low['Low']]

    def _dispose(self):
        self.order = None
        self.indictor = None

    def _cancel_running_order(self, end_price):
        self.margin += self.order.cancel_order(end_price)
        self.orders_history.append(self.order)
        if self.indicator:
            self.indicators.append(self.indicator)
        self._dispose()

    def update_trend(self, day_data):
        if day_data['high'] > self.day_high['high']:
            if self.order:
                self._cancel_running_order(day_data['High'])
            self.trend = 'down'
            self.day_high = day_data
            self.highs_history.append(day_data['High'])

        if day_data['Low'] < self.day_low['Low']:
            if self.order:
                self._cancel_running_order(day_data['Low'])
            self.trend = 'up'
            self.day_low = day_data
            self.lows_history.append(day_data['Low'])
        return self.trend

    def check_indicator_place_order(self, day_data, threshold=5):
        if self.trend == 'up':
            difference = abs(day_data['Open'] - day_data['Low'])
            if difference <= threshold:
                self.indicator = day_data
                self.indicators_history.append(day_data)
        else:
            difference = abs(day_data['Open'] - day_data['High'])
            if difference <= threshold:
                self.indicator = day_data
                self.indicators_history.append(day_data)
        return self.indicator

    def _order_details(self, day_data, Qty, stoploss_threshold, target_threshold):
        price = day_data['Open']
        # Qty = self._get_quantities(Qty)
        if self.trend == 'up':
            type = 'Buy'
            stoploss = self.day_low['Low'] + stoploss_threshold
            target = self.highs_history[-1] - target_threshold
            # target = self.day_high['High'] - target_threshold
        else:
            type = 'Sell'
            stoploss = self.day_high['High'] - stoploss_threshold
            target = self.lows_history[-1] + target_threshold
            # target = self.day_low['Low'] + target_threshold
        place_date = ''
        return [price, type, Qty, stoploss, target, place_date]

    def place_order(self, day_data, Qty=1000, stoploss_threshold=0, target_threshold=20):
        if self.order or (not self.indicator):
            return
        params = self._order_details(
            day_data, Qty, stoploss_threshold, target_threshold)
        self.order = Order(*params)
        self.order.indicator_day = self.indicator
        self.margin -= self.order.invested

    def watch_holdings(self, day_data):
        if not self.order:
            return

        if self.trend == 'up':
            if day_data['Low'] <= self.order.stoploss:
                self._cancel_running_order(self.order.stoploss)
                return
        else:
            if day_data['High'] >= self.order.stoploss:
                self._cancel_running_order(self.order.stoploss)
                return

        if day_data['Low'] <= self.order.target <= day_data['High']:
            self._cancel_running_order(self.order.target)
