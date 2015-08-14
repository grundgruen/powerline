__author__ = "Warren"

from unittest import TestCase
from datetime import timedelta

from zipline.finance import trading

from gg.powerline.utils import tradingcalendar_epex, tradingcalendar_eex
from gg.powerline.exchanges.eex_exchange import EexExchange
from gg.powerline.exchanges.epex_exchange import EpexExchange


class TestTradingCalendarEex(TestCase):
    """
    Tests trading times and trading days for EEX calendar by comparing with
    the benchmark and the DataSource.
    """
    def setUp(self):
        self.exchange = EexExchange()
        trading.environment = self.exchange.env
        trading.environment.update_asset_finder(
            asset_finder=self.exchange.asset_finder)
        self.source = self.exchange.source()

    def test_calendar_vs_environment_eex(self):
        cal_days = trading.environment.benchmark_returns[
            tradingcalendar_eex.start:].index
        bounds = trading.environment.trading_days.slice_locs(
            start=tradingcalendar_eex.start,
            end=cal_days[-1]
            )

        env_days = trading.environment.trading_days[bounds[0]:bounds[1]]
        self.check_days(env_days, cal_days)

    def check_days(self, env_days, cal_days):
        diff = env_days - cal_days
        self.assertEqual(
            len(diff),
            0,
            "{diff} should be empty".format(diff=diff)
        )

        diff2 = cal_days - env_days
        self.assertEqual(
            len(diff2),
            0,
            "{diff} should be empty".format(diff=diff2)
        )

    def test_calendar_vs_databank_eex(self):
        source = self.exchange.source()

        cal_days = trading.environment.benchmark_returns[
            source.start:source.end].index
        row = next(source)
        for expected_dt in cal_days:
            self.assertEqual(expected_dt, row.dt)

            dt_last = row.dt
            while dt_last == row.dt and row.dt != source.end:
                row = next(source)

    def tearDown(self):
        trading.environment = None
        self.source = None


class TestTradingCalendarEpex(TestCase):
    """
    Tests trading times and trading days for EPEX calendar by comparing with
    the benchmark and the DataSource.
    """
    def setUp(self):
        self.exchange = EpexExchange()
        trading.environment = self.exchange.env
        trading.environment.update_asset_finder(
            asset_finder=self.exchange.asset_finder)
        self.source = self.exchange.source()
        self.products = [str(i).zfill(2) + '-' + str(i+1).zfill(2) for i in
                         range(0, 24)]

    def test_calendar_vs_environment_epex(self):
        cal_days = trading.environment.benchmark_returns[tradingcalendar_epex.start:]\
            .index
        bounds = trading.environment.trading_days.slice_locs(
            start=tradingcalendar_epex.start,
            end=cal_days[-1]
            )

        env_days = trading.environment.trading_days[bounds[0]:bounds[1]]
        self.check_days(env_days, cal_days)

    def check_days(self, env_days, cal_days):
        diff = env_days - cal_days
        self.assertEqual(
            len(diff),
            0,
            "{diff} should be empty".format(diff=diff)
        )

        diff2 = cal_days - env_days
        self.assertEqual(
            len(diff2),
            0,
            "{diff} should be empty".format(diff=diff2)
        )

    def test_calendar_vs_databank_epex(self):
        cal_days = trading.environment.benchmark_returns[
            self.source.start:self.source.end-timedelta(days=1)].index
        # TODO insert missing data in database
        for expected_dt in cal_days:
            if str(expected_dt.date()) == '2014-01-30' or \
                    str(expected_dt.date()) == '2014-04-15':
                continue
            for product in self.products:
                # Summer time
                if (str(expected_dt.date()) == '2014-03-29' or
                        str(expected_dt.date()) == '2015-03-28') and product \
                        == '02-03':
                    continue
                # Winter time
                if (str(expected_dt.date()) == '2014-10-25' or
                        str(expected_dt.date()) == '2015-10-24') and product\
                        == '03-04':
                    row = next(self.source)
                    self.assertEqual('02-03b', row.product, expected_dt.date())
                    self.assertEqual(expected_dt.date(), row.dt.date())

                row = next(self.source)
                self.assertEqual(product, row.product, expected_dt.date())
                self.assertEqual(expected_dt.date(), row.dt.date(), row.product)

    def tearDown(self):
        trading.environment = None
        self.source = None
