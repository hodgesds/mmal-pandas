from __future__ import print_function
from mmal.client import Client
from mmal.pandas import parse_reply


client = Client('localhost', 8080)


# ping request example
pong_reply = client.ping_request([[]])
print(pong_reply)

# path request example
path_reply = client.path_request(
    [['example']],
)

print(path_reply)

# time series request example
ts_reply = client.ts_request(
    [['wind']],
    cols = ['timestamp', 'speed', 'direction'],
)

print(ts_reply)

dfs = parse_reply(ts_reply)
print(dfs)
