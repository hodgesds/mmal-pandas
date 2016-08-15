# Pandas bindings for MMAL

This package provides an easy to use package for interacting with the MMAL rpc
layer and pandas. It provides utility methods to return lists of dataframes
from time series requests.

Here is a basic eample that uses the MMAL client to retrieve a time series from
MMAL and return that time series as a dataframe.

# Installation

`pip install mmal-pandas`

# Example

First create a sqlite database and add an outlier to the last observation on the
`wind` table:

```sh
$ cat example.sql
CREATE TABLE IF NOT EXISTS temp(timestamp INTEGER PRIMARY KEY, temp INTEGER);
INSERT INTO temp VALUES(1470600282123000000, 10);
INSERT INTO temp VALUES(1470600282218000000, 11);
INSERT INTO temp VALUES(1470600282377000000, 12);
INSERT INTO temp VALUES(1470600282450000000, 11);
CREATE TABLE IF NOT EXISTS wind(timestamp TEXT PRIMARY KEY, speed INTEGER, direction REAL);
INSERT INTO wind VALUES('2016-08-07T16:00:20-04:00', 10, 162.3);
INSERT INTO wind VALUES('2016-08-07T16:00:20-05:00', 11, 183.8);
INSERT INTO wind VALUES('2016-08-07T16:00:20-06:00', 12, 190.1);
INSERT INTO wind VALUES('2016-08-07T16:00:20-07:00', 15, 220.4);
INSERT INTO wind VALUES('2016-08-07T16:00:20-08:00', 13, 180.2);
INSERT INTO wind VALUES('2016-08-07T16:00:20-09:00', 10, 215.0);
INSERT INTO wind VALUES('2016-08-07T16:00:20-10:00', 7, 236.3);
INSERT INTO wind VALUES('2016-08-07T16:00:20-11:00', 9, 220.9);
INSERT INTO wind VALUES('2016-08-07T16:00:20-12:00', 8, 263.7);
INSERT INTO wind VALUES('2016-08-07T16:00:20-13:00', 10, 233.4);
INSERT INTO wind VALUES('2016-08-07T16:00:20-14:00', 11, 212.2);
INSERT INTO wind VALUES('2016-08-07T16:00:20-15:00', 13, 193.9);
INSERT INTO wind VALUES('2016-08-07T16:00:20-16:00', 12, 178.7);
INSERT INTO wind VALUES('2016-08-07T16:00:20-17:00', 11, 154.3);
INSERT INTO wind VALUES('2016-08-07T16:00:20-18:00', 100000, 220.1);
```

```sh
$ cat example.sql | sqlite3 example.sqlite
```

Now that we have a database lets use MMAL server as a rpc transport layer.

```sh
$ mmal server -d 'sqlite:///example.sqlite'
```

Once you have a server started you can test the connection to the RPC server
with a **ping** request:

```python
from __future__ import print_function
from mmal.client import Client
from mmal.pandas import parse_reply
from scipy import stats
import numpy as np


client = Client('localhost', 8080)


# ping request example
pong_reply = client.ping_request([[]])
print(pong_reply)
>>> id: "ab0805e6-627f-11e6-a4d1-44850017d653"
>>> pong_reply {
>>>   pong: "PONG"
>>> }
```

You can then inspect a table by doing a **path** request:

```python
# path request example
path_reply = client.path_request(
    [['temp']],
)

print(path_reply)
>>> type: PATH
>>> path_reply {
>>>   paths {
>>>     parts: "temp"
>>>     columns: "timestamp"
>>>     columns: "temp"
>>>   }
>>> }
```

The pandas bindings are used when doing a **ts_request**. Calling `parse_reply`
on a `ts_request` will return a ***list of dataframes***. **NOTE** that the
timestamp column is ***always*** expected to be the first column or zero
indexed in the case of python.

```python
# time series request example
ts_reply = client.ts_request(
    [['temp']],
    cols  = ['timestamp', 'temp'],
    limit = 100,
)

print(ts_reply)
>>> id: "25eea804-6281-11e6-8cee-44850017d653"
>>> type: TIMESERIES
>>> ts_reply {
>>>   time_series {
>>>     columns {
>>>       int64s: 1470600282123000000
>>>       int64s: 1470600282218000000
>>>       int64s: 1470600282377000000
>>>       int64s: 1470600282450000000
>>>       type: TYPE_INT64
>>>       name: "timestamp"
>>>     }
>>>     columns {
>>>       int64s: 10
>>>       int64s: 11
>>>       int64s: 12
>>>       int64s: 11
>>>       type: TYPE_INT64
>>>       name: "temp"
>>>     }
>>>   }
>>>   paths {
>>>     parts: "temp"
>>>     columns: "timestamp"
>>>     columns: "temp"
>>>   }
>>> }

dfs = parse_reply(ts_reply)
print(dfs)
>>> [                         temp
>>> 2016-08-07 20:04:42.123    10
>>> 2016-08-07 20:04:42.218    11
>>> 2016-08-07 20:04:42.377    12
>>> 2016-08-07 20:04:42.450    11]
```

An even more powerful method is the `apply` method on the client. The `apply`
function will 'walk' the database and apply a function on the returned reply
objects. This becomes extremely powerful when using `parse_reply` as each table
then can automatically be return as a dataframe.

```python
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
```

# Using GLOS Data

Grabbing data from the GLOS data portal is also a possibility.
[Here](http://www.greatlakesbuoys.org/select_range.php?station=45172) is an
example data set which provides some buoy data. To use this data with pandas it
can be downloaded from the GLOS data port via the web interface or with curl.
Here is an example using curl:

```sh
$ curl 'http://www.greatlakesbuoys.org/genData.php' -H 'Referer: http://www.greatlakesbuoys.org/select_range.php?station=45172' -H 'Connection: keep-alive' --data 'startMonth=06&startDay=1&startYear=2015&endMonth=08&endDay=14&endYear=2016&station=45172' --compressed
$ head BuoyData.csv 
ID (), STATION (), DATE (), FM64II (), FM64XX (), FM64K1 (), FM64K2 (), FM64K3 (), FM64K4 (), FM64K5 (), FM64K6 (), SPCOND (), YSITDS (), PH (), ORP (), YSITURBNTU (), YSITSS (), YSICHLRAW (), YSICHLRFU (), YSICHLUGL (), YSIBGARAW (), YSIBGARFU (), YSIBGAUGL (), ERH (), WTMP1 (&deg;C)
30365, leorgn, 01/01/2016 00:00:00, 820, 99, 7, 0, 3, 9, 5, 4, 228.39, 0.15, 8.02, 573.62, 40.25, 0, 0.38, 0.59, 2.94, -0.32, 0.18, 0.37, 47.1, 3.69
30366, leorgn, 01/01/2016 00:10:00, 820, 99, 7, 0, 3, 9, 5, 4, 229.28, 0.15, 8.03, 572.27, 43.23, 0, 0.38, 0.59, 2.95, -0.27, 0.23, 0.43, 47.1, 3.69
30367, leorgn, 01/01/2016 00:20:00, 820, 99, 7, 0, 3, 9, 5, 4, 230.11, 0.15, 8.03, 571.11, 47.97, 0, 0.42, 0.63, 3.12, -0.27, 0.23, 0.42, 47.06, 3.68
30368, leorgn, 01/01/2016 00:30:00, 820, 99, 7, 0, 3, 9, 5, 4, 230.91, 0.15, 8.03, 569.83, 42.47, 0, 0.4, 0.61, 3.05, -0.29, 0.21, 0.4, 47.03, 3.68
30369, leorgn, 01/01/2016 00:40:00, 820, 99, 7, 0, 3, 9, 5, 4, 232.02, 0.15, 8.03, 568.44, 45.6, 0, 0.43, 0.65, 3.18, -0.27, 0.23, 0.42, 47.03, 3.68
30370, leorgn, 01/01/2016 00:50:00, 820, 99, 7, 0, 3, 9, 5, 4, 232.77, 0.15, 8.02, 567.23, 46.24, 0, 0.45, 0.67, 3.27, -0.29, 0.22, 0.41, 47.1, 3.67
30371, leorgn, 01/01/2016 01:00:00, 820, 99, 7, 0, 3, 9, 5, 4, 232.82, 0.15, 8.02, 565.75, 44.72, 0, 0.45, 0.67, 3.29, -0.3, 0.21, 0.39, 47.06, 3.67
30372, leorgn, 01/01/2016 01:10:00, 820, 99, 7, 0, 3, 9, 5, 4, 232.44, 0.15, 8.02, 564.6, 44.24, 0, 0.43, 0.64, 3.18, -0.3, 0.2, 0.39, 47.03, 3.67
30373, leorgn, 01/01/2016 01:20:00, 820, 99, 7, 0, 3, 9, 5, 4, 232.66, 0.15, 8.03, 563.45, 46.27, 0, 0.46, 0.68, 3.32, -0.28, 0.22, 0.41, 47.1, 3.67

```

Once the data is downloaded it then can be used with pandas by reading the data
into a dataframe:

```python
import pandas as pd
>>> df = pd.read_csv("BuoyData.csv")
>>> df.head(2)
   ID ()  STATION ()               DATE ()   FM64II ()   FM64XX ()  \
0  30365      leorgn   01/01/2016 00:00:00         820          99   
1  30366      leorgn   01/01/2016 00:10:00         820          99   

    FM64K1 ()   FM64K2 ()   FM64K3 ()   FM64K4 ()   FM64K5 ()  \
0           7           0           3           9           5   
1           7           0           3           9           5   

        ...          YSITURBNTU ()   YSITSS ()   YSICHLRAW ()   YSICHLRFU ()  \
0       ...                  40.25           0           0.38           0.59   
1       ...                  43.23           0           0.38           0.59   

    YSICHLUGL ()   YSIBGARAW ()   YSIBGARFU ()   YSIBGAUGL ()   ERH ()  \
0           2.94          -0.32           0.18           0.37     47.1   
1           2.95          -0.27           0.23           0.43     47.1   

    WTMP1 (&deg;C)  
0             3.69  
1             3.69  

[2 rows x 25 columns]
>>> df.iloc[0:5,0:6]
   ID ()  STATION ()               DATE ()   FM64II ()   FM64XX ()   FM64K1 ()
0  30365      leorgn   01/01/2016 00:00:00         820          99           7
1  30366      leorgn   01/01/2016 00:10:00         820          99           7
2  30367      leorgn   01/01/2016 00:20:00         820          99           7
3  30368      leorgn   01/01/2016 00:30:00         820          99           7
4  30369      leorgn   01/01/2016 00:40:00         820          99           7
>>> df.iloc[0:5,0:6].mean()
ID ()         30367.0
 FM64II ()      820.0
 FM64XX ()       99.0
 FM64K1 ()        7.0
dtype: float64
```

The data is loaded but there is a slight problem, the dates need to be
transformed before any useful work can be done. First the messy column name `
DATE()` will be coerced to python datetime objects using the `to_datetime`
method. Next, the index of the dataframe will be updated for these datetimes.

```python
>>> 
>>> dt = pd.to_datetime(df[u' DATE ()'])
>>> df.index = dt
>>> df.iloc[0:5,0:6]
                     ID ()  STATION ()               DATE ()   FM64II ()  \
 DATE ()                                                                   
2016-01-01 00:00:00  30365      leorgn   01/01/2016 00:00:00         820   
2016-01-01 00:10:00  30366      leorgn   01/01/2016 00:10:00         820   
2016-01-01 00:20:00  30367      leorgn   01/01/2016 00:20:00         820   
2016-01-01 00:30:00  30368      leorgn   01/01/2016 00:30:00         820   
2016-01-01 00:40:00  30369      leorgn   01/01/2016 00:40:00         820   

                      FM64XX ()   FM64K1 ()  
 DATE ()                                     
2016-01-01 00:00:00          99           7  
2016-01-01 00:10:00          99           7  
2016-01-01 00:20:00          99           7  
2016-01-01 00:30:00          99           7  
2016-01-01 00:40:00          99           7  
```

Finally, a similar analysis can be done above using MMAL.
