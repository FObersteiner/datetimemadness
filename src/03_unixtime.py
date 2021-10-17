#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Oct  5 20:07:11 2021

@author: flonblnx
"""
from datetime import datetime, timezone

now_utc = datetime.now(timezone.utc)
print(now_utc)
# 2021-10-17 09:40:47.170662+00:00

unix = now_utc.timestamp()
print(unix)
# 1634463647.170662

back_utc = datetime.fromtimestamp(unix, tz=timezone.utc)
print(back_utc)
# 2021-10-17 09:40:47.170662+00:00


back = datetime.fromtimestamp(unix)
print(back)
# 2021-10-17 11:40:47.170662

naive = datetime(2021, 10, 17)
print(naive)
# 2021-10-17 00:00:00
unix = naive.timestamp()
print(datetime.fromtimestamp(unix, timezone.utc))
# 2021-10-16 22:00:00+00:00