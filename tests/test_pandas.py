from __future__ import absolute_import
import unittest
import pandas as pd
from nose.tools import ok_
from mmal.pandas import to_df, parse_reply
from mmal.proto import *

class TestPandas(unittest.TestCase):

    def test_to_df(self):
        ts = TimeSeries()
        idx = ts.Column()
        idx.strings.extend([
            "2016-01-01",
        ])
        idx.type = TYPE_STRING
        col1 = ts.Column()
        col1.strings.extend([
            "test"
        ])
        col1.type = TYPE_STRING
        ts.columns.extend([idx, col1])

        df = to_df(ts)
        ok_(isinstance(df, pd.DataFrame))

    def parse_reply(self):
        # PONG reply
        reply = Reply()
        reply.type = reply.PONG
        eq_(None, parse_reply(reply))

        # PATH reply
        reply = Reply()
        reply.type = reply.PATH
        eq_(None, parse_reply(reply))

        # TIMESERIES reply
        reply = Reply()
        reply.type = reply.TIMESERIES

        ts = TimeSeries()
        idx = ts.Column()
        idx.strings.extend([
            "2016-01-01",
        ])
        idx.type = TYPE_STRING
        col1 = ts.Column()
        col1.strings.extend([
            "test"
        ])
        col1.type = TYPE_STRING
        ts.columns.extend([idx, col1])

        reply.ts_reply.time_series.extend([ts])

        dfs = parse_reply(reply)
        eq_(1, len(dfs))

if __name__ == '__main__':
    unittest.main()

ts = TimeSeries()
idx = ts.Column()
idx.strings.extend([
    "2016-01-01",
])
idx.type = TYPE_STRING
col1 = ts.Column()
col1.strings.extend([
    "test"
])
col1.type = TYPE_STRING
ts.columns.extend([idx, col1])

df = to_df(ts)
