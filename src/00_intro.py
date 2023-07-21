#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Oct  5 19:29:34 2021

@author: flonblnx
"""
from datetime import datetime

now = datetime.now()
print(now)
# prints the string representation of the datetime object, for example
# 2021-10-05 19:32:04.898003

# or with a bit of formatting:
print(f"the current time is {now.time()}, on {now.date()}")
# the current time is 19:32:04.898003, on 2021-10-05

print(repr(now))
# datetime.datetime(2021, 10, 5, 19, 32, 4, 898003)


from datetime import timezone

now_utc = datetime.now(timezone.utc)
print(now_utc)
# 2021-10-05 17:32:04.898176+00:00
print(repr(now_utc))
# datetime.datetime(2021, 10, 5, 17, 32, 4, 898176, tzinfo=datetime.timezone.utc)
