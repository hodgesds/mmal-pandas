# Pandas bindings for MMAL

This package provides an easy to use package for interacting with the MMAL rpc
layer and pandas. It provides utility methods to return lists of dataframes
from time series requests.

Here is a basic eample that uses the MMAL client to retrieve a time series from
MMAL and return that time series as a dataframe:

```python
from __future__ import print_function
from mmal.client import Client
from mmal.pandas import parse_reply

client = Client('localhost', 8080)

# time series request example
ts_reply = client.ts_request(
    [['wind']],
    cols = ['timestamp', 'speed', 'direction'],
)

print(ts_reply)

dfs = parse_reply(ts_reply)
print(dfs)
[                      direction  speed
2016-08-07 20:00:20  120.300003     10
2016-08-07 21:00:20  183.800003     11
2016-08-07 22:00:20   90.099998     12
2016-08-07 23:00:20  220.399994     11]
```
