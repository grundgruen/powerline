__author__ = 'Warren'

from unittest import TestCase

import numpy as np
import pandas as pd

from zipline.history.history import HistorySpec
from zipline.protocol import BarData

from gg.powerline.history.history_container import EpexHistoryContainer
from gg.powerline.exchanges.epex_exchange import EpexExchange


def date_range(start_date, end_date):
    '''This is a consistent range of datetimes.

    As with the built-in range, the resulting iterator stops with the last date
    before the end_date
    '''
    for n in range((end_date - start_date).days):
        yield start_date + pd.Timedelta(days=n)


class TestHistoryDateRows(TestCase):
    def setUp(self):
        self.start_date = pd.Timestamp('2015-06-01', tz='Europe/Berlin').\
            tz_convert('UTC')
        self.end_date = pd.Timestamp('2015-06-30', tz='Europe/Berlin').\
            tz_convert('UTC')

        source_start = self.start_date - pd.Timedelta(hours=2)

        self.hourly_products = ["%(a)02d-%(b)02d" % {'a': i, 'b': i+1}
                                for i in range(24)]
        self.quarter_product_tags = ["Q"+str(i) for i in range(1, 5)]

        self.exchange = EpexExchange(start=self.start_date, end=self.end_date)
        self.env = self.exchange.env

        asset_metadata = {}
        self.env.write_data(futures_data=asset_metadata)

        self.BAR_COUNT = 3
        history_spec = HistorySpec(bar_count=self.BAR_COUNT, frequency='1m',
                                   field='price', ffill=False,
                                   data_frequency='minute', env=self.env)
        history_specs = {}
        history_specs[history_spec.key_str] = history_spec

        self.container = EpexHistoryContainer(history_specs, None,
                                              source_start, 'minute',
                                              env=self.env)

        self.market_forms = ['epex_auction', 'intraday', 'aepp', 'rebap']

    def test_date_rows_simple(self):
        day1 = pd.Timestamp('2015-06-06')
        day5 = pd.Timestamp('2015-06-10')

        data = {}
        rolling_sid = 1
        for single_date in date_range(day1, day5):
            data[rolling_sid] = {
                'dt': single_date,
                'price': np.random.uniform(0, 100),
                'market': 'epex_auction',
                'product': self.hourly_products[np.random.randint(0, 24)],
                'day': single_date,
                'sid': rolling_sid
            }
            rolling_sid += 1

        for current_sid in data:
            current_data = data[current_sid]
            bar = BarData({current_sid: current_data})
            self.container.update(bar, current_data['dt'])
            history = self.container.get_history()

            for market in self.market_forms:
                self.assertLessEqual(len(history[market]), self.BAR_COUNT)

            self.assertEqual(history[current_data['market']]
                             [current_data['product']].ix[current_data['day']],
                             current_data['price'])


class TestHistoryPerSimpleMockData(TestCase):
    def setUp(self):
        self.start_date = pd.Timestamp('2015-06-25', tz='Europe/Berlin').\
            tz_convert('UTC')
        self.end_date = pd.Timestamp('2015-06-28', tz='Europe/Berlin').\
            tz_convert('UTC')

        source_start = self.start_date - pd.Timedelta(hours=2)

        self.hourly_products = ["%(a)02d-%(b)02d" % {'a': i, 'b': i+1}
                                for i in range(24)]
        self.quarter_product_tags = ["Q"+str(i) for i in range(1, 5)]

        self.exchange = EpexExchange(start=self.start_date, end=self.end_date)
        self.env = self.exchange.env

        asset_metadata = {}
        self.env.write_data(futures_data=asset_metadata)

        self.BAR_COUNT = 3
        history_spec = HistorySpec(bar_count=self.BAR_COUNT, frequency='1m',
                                   field='price', ffill=False,
                                   data_frequency='minute', env=self.env)
        history_specs = {}
        history_specs[history_spec.key_str] = history_spec

        self.container = EpexHistoryContainer(history_specs, None,
                                              source_start, 'minute',
                                              env=self.env)

        self.market_forms = ['epex_auction', 'intraday', 'aepp', 'rebap']

        self.hourly_products = ["%(a)02d-%(b)02d" % {'a': i, 'b': i+1}
                                for i in range(24)]
        self.quarter_product_tags = ["Q"+str(i) for i in range(1, 5)]

    def test_full_data_history(self):
        data = {}
        rolling_sid = 1
        for single_date in date_range(self.start_date, self.end_date):
            for current_hour in range(24):
                data[rolling_sid] = {
                    'dt': single_date,
                    'price': np.random.uniform(0, 100),
                    'market': self.market_forms[0],
                    'product': self.hourly_products[current_hour],
                    'day': single_date,
                    'sid': rolling_sid
                }
                rolling_sid += 1
                for market in self.market_forms[1:4]:
                    for current_quarter in self.quarter_product_tags:
                        data[rolling_sid] = {
                            'dt': single_date,
                            'price': np.random.uniform(0, 100),
                            'market': market,
                            'product': "%02d" % current_hour + current_quarter,
                            'day': single_date,
                            'sid': rolling_sid
                        }
                        rolling_sid += 1

        for current_sid in data:
            current_data = data[current_sid]
            bar = BarData({current_sid: current_data})
            self.container.update(bar, current_data['dt'])
            history = self.container.get_history()

            for market in self.market_forms:
                self.assertLessEqual(len(history[market]), self.BAR_COUNT)

            self.assertEqual(history[current_data['market']]
                             [current_data['product']].ix[current_data['day']],
                             current_data['price'])

    def test_sparse_data(self):
        data = {}
        rolling_sid = 1
        for single_date in date_range(self.start_date, self.end_date):
            data[rolling_sid] = {
                'dt': single_date,
                'price': np.random.uniform(0, 100),
                'market': 'epex_auction',
                'product': self.hourly_products[np.random.randint(0, 24)],
                'day': single_date,
                'sid': rolling_sid
            }
            rolling_sid += 1

        for current_sid in data:
            current_data = data[current_sid]
            bar = BarData({current_sid: current_data})
            self.container.update(bar, current_data['dt'])
            history = self.container.get_history()

            for market in self.market_forms:
                self.assertLessEqual(len(history[market]), self.BAR_COUNT)

            self.assertEqual(history[current_data['market']]
                             [current_data['product']].ix[current_data['day']],
                             current_data['price'])

    def test_simple_price_update(self):
        day1 = self.start_date
        day2 = self.start_date + pd.Timedelta(days=1)

        data = {1: {'dt': day1,
                    'price': 5,
                    'market': 'aepp',
                    'product': '01Q1',
                    'day': day1,
                    'sid': 1},
                2: {'dt': day2,
                    'price': 10,
                    'market': 'aepp',
                    'product': '01Q1',
                    'day': day2,
                    'sid': 2},
                3: {'dt': day2,
                    'price': 7,
                    'market': 'aepp',
                    'product': '01Q1',
                    'day': day1,
                    'sid': 3}
                }

        for current_sid in data:
            current_data = data[current_sid]
            bar = BarData({current_sid: current_data})
            self.container.update(bar, current_data['dt'])

        history = self.container.get_history()

        self.assertEqual(history['aepp']['01Q1'].ix[day1], 7)
        self.assertEqual(history['aepp']['01Q1'].ix[day2], 10)
