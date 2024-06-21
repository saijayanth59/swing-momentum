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
        self.indicator = False  # bool
        self.current_trend_order = False

        self.indicators_history = []
        self.orders_history = []
        self.highs_history = [day_high['High']]
        self.lows_history = [day_low['Low']]

    def _dispose(self):
        self.order = None
        self.indictor = False

    def _cancel_running_order(self, end_price, date):
        self.margin += self.order.cancel_order(end_price)
        self.order.close = date
        self.orders_history.append(self.order)
        self._dispose()

    def update_trend(self, day_data):
        if day_data['High'] > self.day_high['High']:
            if self.order:
                if self.order.type == 'Buy':
                    self._cancel_running_order(
                        day_data['High'], date=day_data.index)
                else:
                    self._cancel_running_order(
                        day_data['Low'], date=day_data.index)
            self.trend = 'down'
            self.day_high = day_data
            self.current_trend_order = False
            self.highs_history.append(day_data['High'])
            # print("Trend Change", self.margin)

        if day_data['Low'] < self.day_low['Low']:
            if self.order:
                self._cancel_running_order(
                    day_data['Close'], date=day_data.index)
            self.trend = 'up'
            self.day_low = day_data
            self.current_trend_order = False
            self.lows_history.append(day_data['Low'])
            # print("Trend Change", self.margin)
        return self.trend

    def check_indicator(self, day_data, threshold=5):

        if self.order or (self.indicator):
            return
        if self.trend == 'up':
            difference = abs(day_data['Open'] - day_data['Low'])
            if difference <= threshold:
                self.indicator = True
                self.indicators_history.append(day_data)
        else:
            difference = abs(day_data['Open'] - day_data['High'])
            if difference <= threshold:
                self.indicator = True
                self.indicators_history.append(day_data)
        return self.indicator

    def _get_quantities(self, price):
        return (self.margin) // price

    def _order_details(self, day_data, Qty, stoploss_threshold, target_threshold):
        price = day_data['Open']
        Qty = self._get_quantities(price)
        if self.trend == 'up':
            type = 'Buy'
            stoploss = self.day_low['Low'] + stoploss_threshold
            target = self.highs_history[-1] - target_threshold
            target = day_data['Open'] + 80
            # target = self.day_high['High'] - target_threshold
        else:
            type = 'Sell'
            stoploss = self.day_high['High'] - stoploss_threshold
            target = self.lows_history[-1] + target_threshold
            target = day_data['Open'] - 80
            # target = self.day_low['Low'] + target_threshold
        place_date = ''
        return [price, type, Qty, stoploss, target, place_date]

    def place_order(self, day_data, Qty=1000, stoploss_threshold=0, target_threshold=20):
        if not self.indicator:
            return
        if self.order:
            return
        if self.current_trend_order:
            return
        params = self._order_details(
            day_data, Qty, stoploss_threshold, target_threshold)
        self.order = Order(*params)
        self.order.place = day_data.name
        self.order.indicator_day = self.indicators_history[-1]
        self.margin -= self.order.invested
        self.current_trend_order = True

    def watch_holdings(self, day_data):
        if not self.order:
            return

        if self.trend == 'up':
            if day_data['Low'] <= self.order.stoploss:
                self._cancel_running_order(
                    self.order.stoploss, date=day_data.index)
                print('Fail')
                return
        else:
            if day_data['High'] >= self.order.stoploss:
                self._cancel_running_order(
                    self.order.stoploss, date=day_data.name)
                print("Fail")
                return

        if day_data['Low'] <= self.order.target <= day_data['High']:
            print("Target Hit", day_data.name, self.order.place)
            self._cancel_running_order(self.order.target, date=day_data.index)
