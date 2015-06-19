__author__ = "Warren"

from abc import ABCMeta, abstractmethod

from zipline.finance.trading import TradingEnvironment
from gg.powerline.data.loader_power import load_market_data


# TODO use properties where appropriate (compare commission)
class Exchange(object, metaclass=ABCMeta):
    """
    A class to collect all exchange-relevant info.
    """
    def __init__(self):
        self.bm_symbol = self.insert_benchmark()
        self.exchange_tz = "Europe/Berlin"
        self.calendar = self.insert_calendar()
        self.load = load_market_data
        self.env = self.insert_env()
        self.asset_finder = self.insert_asset_finder()
        self.source = self.insert_source()

    def insert_env(self):
        """
        passing relevant exchange objects to the environment
        """
        return TradingEnvironment(bm_symbol=self.bm_symbol,
                                  exchange_tz=self.exchange_tz,
                                  env_trading_calendar=self.calendar,
                                  load=self.load)

    @abstractmethod
    def insert_source(self):
        """defined in subclass"""

    @abstractmethod
    def insert_asset_finder(self):
        """defined in subclass"""

    @abstractmethod
    def insert_benchmark(self):
        """defined in subclass"""

    @abstractmethod
    def insert_calendar(self):
        """defined in subclass"""

    @property
    @abstractmethod
    def commission(self):
        """defined in subclass"""
