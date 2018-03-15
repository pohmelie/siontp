# siontp
Simple sans-io ntp client with couple backends:
* blocking (`socket` module)
* non-blocking (`asyncio` module)

## Reasons
* need simple method to determine current absolute time from network
* [`ntplib`](https://pypi.org/project/ntplib/) do not support `asyncio`

## Requirements
* python3.5+
* `aiodns` (if you want absolute `asyncio` solution without extra threads)

## Installation
* sync: `python -m pip install siontp[requests]`
* async: `python -m pip install siontp[aiohttp]`

## Usage
Library is pretty similar to [`ntplib`](https://pypi.org/project/ntplib/), with exception, that packet timestamps are
not in NTP timestamp format (epoch 1900 year), but in system timestamp (epoch 1970 for most systems).

### Blocking
``` python
>>> import siontp
>>> siontp.request().remote_datetime
datetime.datetime(2018, 3, 6, 2, 36, 8, 808154)
```

### Non-blocking
``` python
>>> import siontp
>>> (await siontp.arequest()).remote_datetime
datetime.datetime(2018, 3, 6, 2, 36, 8, 808154)
```

Checkout `protocol.py` for more values of response.
