from datetime import timedelta
import pandas as pd
from zipline.algorithm import TradingAlgorithm
from zipline.finance.commission import PerShare
from zipline.finance.slippage import FixedSlippage
from gg.powerline.finance.auction import TradingAlgorithmAuction, \
    BeforeEpexAuction, auction
from gg.messaging.json_producer import JsonProducer


class TestAuctionAlgorithm(TradingAlgorithmAuction):
    """
    This algorithm will send a specified number of orders, to allow unit tests
    to verify the orders sent/received, transactions created, and positions
    at the close of a simulation.
    """

    def initialize(self,
                   sid,
                   amount,
                   order_count,
                   day,
                   products,
                   sid_filter=None,
                   slippage=None,
                   commission=None):
        self.count = order_count
        self.asset = self.sid(sid)
        self.amount = amount
        self.day = day
        self.incr = 0
        self.products = products

        if sid_filter:
            self.sid_filter = sid_filter
        else:
            self.sid_filter = [self.asset.sid]

        if slippage is not None:
            self.set_slippage(slippage)

        if commission is not None:
            self.set_commission(commission)

        self.schedule_function(func=auction, time_rule=BeforeEpexAuction(
            minutes=30))

    def handle_data(self, data):
        pass


class TestEpexMessagingAlgorithm(TradingAlgorithmAuction):
    """
    This algorithm will send a specified number of orders, to allow unit tests
    to verify the orders sent/received, transactions created, and positions
    at the close of a simulation.
    """

    def initialize(self,
                   sid,
                   amount,
                   order_count,
                   day,
                   products,
                   sid_filter=None,
                   slippage=None,
                   commission=None,
                   ):
        self.products = products
        self.count = order_count
        self.asset = self.sid(sid)
        self.amount = amount
        self.day = day
        self.incr = 0

        if sid_filter:
            self.sid_filter = sid_filter
        else:
            self.sid_filter = [self.asset.sid]

        if slippage is not None:
            self.set_slippage(slippage)

        if commission is not None:
            self.set_commission(commission)

        self.schedule_function(func=auction_message,
                               time_rule=BeforeEpexAuction(minutes=30))

        self.producer = JsonProducer()

    def handle_data(self, data):
        self.producer.run(self.datetime.date(),
                          self.perf_tracker.cumulative_performance.to_dict())


def auction_message(algo, data):
    """
    Calculates the current day and then places an auction order for the
    following day.
    """
    day = algo.get_datetime().date() + timedelta(days=1)
    algo.order_auction(day=day, amounts=algo.amount)
    algo.incr += 1


class TestFekAlgo(TestAuctionAlgorithm):

    def initialize(self,
                   sid,
                   amount,
                   order_count,
                   day,
                   products,
                   sid_filter=None,
                   slippage=None,
                   commission=None):
        self.count = order_count
        self.asset = self.sid(sid)
        self.amount = amount
        self.day = day
        self.incr = 0
        self.products = products
        self.prog = pd.DataFrame()

        if sid_filter:
            self.sid_filter = sid_filter
        else:
            self.sid_filter = [self.asset.sid]

        if slippage is not None:
            self.set_slippage(slippage)

        if commission is not None:
            self.set_commission(commission)

        self.schedule_function(func=auction, time_rule=BeforeEpexAuction(
            minutes=30))

    def handle_data(self, data):
        self.prog_update(data)


class FlippingAlgorithm(TradingAlgorithm):

    def initialize(self,
                   sid,
                   amount,
                   slippage,
                   commission):
        self.asset = self.sid(sid)
        self.amount = amount
        self.sid_filter = [self.asset.sid]
        self.set_slippage(slippage)
        self.set_commission(commission)

    def handle_data(self, data):

        if len(self.portfolio.positions) > 0:
            if self.portfolio.positions[self.asset.sid]["amount"] > 0:
                self.order_target(self.asset, -self.amount)
            else:
                self.order_target(self.asset, 0)
        else:
            self.order_target(self.asset, self.amount)

        # self.perf_tracker.position_tracker._update_asset(self.asset.sid)
        # self.perf_tracker.update_performance()
