from __future__ import print_function
from mmal.client import Client
from mmal.pandas import parse_reply
from scipy import stats
import numpy as np


client = Client('localhost', 8080)


# ping request example
pong_reply = client.ping_request([[]])
print(pong_reply)

# path request example
path_reply = client.path_request(
    [['temp']],
)

print(path_reply)

# time series request example
ts_reply = client.ts_request(
    [['temp']],
    cols  = ['timestamp', 'temp'],
    limit = 100,
)

print(ts_reply)

dfs = parse_reply(ts_reply)
print(dfs)


# here is a function that filters outliers across tables. It first parses the
# reply by calling parse_reply and then returns a dataframe with all outliers (z
# score > 3) removed.
def outlier_filter(reply):
    for df in  parse_reply(reply):
        # return cleaned dataframe without outliers
        return df[(np.abs(stats.zscore(df)) < 3).all(axis=1)]

# The apply function on a client will 'walk' the database and return the reply
# object for each table. This is very useful in applying a function across all
# tables in a database.
for cleaned_df in client.apply([['/']], outlier_filter, limit=100):
    print(cleaned_df)
