from zipline.finance import trading

from powerline.utils import tradingcalendar_eex
from powerline.utils import tradingcalendar_epex
from powerline.exchanges.exchange import EexExchange, EpexExchange
from unittest import TestCase
from nose.tools import nottest


class TestTradingCalendarEex(TestCase):
    def setUp(self):
        trading.environment = EexExchange.env
        trading.environment.update_asset_finder(
            asset_finder=EexExchange.asset_finder)
        self.source = EexExchange.data_source()

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
        source = self.source

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
    def setUp(self):
        trading.environment = EpexExchange.env
        trading.environment.update_asset_finder(
            asset_finder=EpexExchange.asset_finder)
        self.source = EpexExchange.data_source()

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

    #@nottest
    def test_calendar_vs_databank_epex(self):
        cal_days = trading.environment.benchmark_returns[self.source.start:self.source.end].index

        row = next(self.source)
        for expected_dt in cal_days:
            print(row.dt)
            self.assertEqual(expected_dt, row.dt)
            dt_last = row.dt
            while dt_last == row.dt and row.dt != self.source.end:
                row = next(self.source)

    def tearDown(self):
        trading.environment = None
        self.source = None
