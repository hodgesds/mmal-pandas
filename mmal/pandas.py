from __future__ import absolute_import
import pandas as pd
from mmal.proto import *
from mmal.utils import get_col


def parse_reply(reply):
    if not reply.type == reply.TIMESERIES:
        return

    dfs = []
    for ts in reply.ts_reply.time_series:
        dfs.append(to_df(ts))

    return dfs


def to_df(timeseries):
    df = pd.DataFrame(
        data = dict(
	    (col.name or x, get_col(timeseries ,x))
            for x, col in enumerate(timeseries.columns[:][1:], 1)
        ),
        index = [pd.to_datetime(get_col(timeseries, 0)[:])],
    )

    return df
