#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Oct  5 19:33:04 2021

@author: flonblnx
"""
from datetime import datetime, timezone

# on some systems, the locale needs to be set; we use English here
import locale

locale.setlocale(locale.LC_TIME, "en_GB.utf8")
# locale string (2nd parameter) is platform-specific !


# -----------------------------------------------------------------------------
# basics, from string to datetime

s = "10/14/1986 18:00"
dt = datetime.strptime(s, "%m/%d/%Y %H:%M")
print(repr(dt))
# datetime.datetime(1986, 10, 14, 18, 0)

# or another one, just time in AM/PM format:
s = "9:15 PM"
dt = datetime.strptime(s, "%I:%M %p")
print(repr(dt))
# datetime.datetime(1900, 1, 1, 21, 15)
# note that a default date was added

s = "10.14.1986"
try:
    dt = datetime.strptime(s, "%m/%d/%Y")
except ValueError as e:
    print(e)
    # time data '10.14.1986' does not match format '%m/%d/%Y'


# -----------------------------------------------------------------------------
# ISO format (ISO8601)

s = "2020-07-30T13:17:00.333+03:00"
dt = datetime.fromisoformat(s)
print(repr(dt))
# datetime.datetime(2020, 7, 30, 13, 17, 0, 333000, tzinfo=datetime.timezone(datetime.timedelta(seconds=10800)))

# UTC offset of zero hours is parsed to UTC:
s = "1970-01-01T12:18:00+00:00"
dt = datetime.fromisoformat(s)
print(repr(dt))
# datetime.datetime(1970, 1, 1, 12, 18, tzinfo=datetime.timezone.utc)


# -----------------------------------------------------------------------------
# GMT / UTC pitfall

s = "10.14.1986 9:15 PM GMT"
dt = datetime.strptime(s, "%m.%d.%Y %I:%M %p %Z")
print(repr(dt))
# datetime.datetime(1986, 10, 14, 21, 15) # GMT is lost!
print(dt.tzinfo)
# None

dt = datetime.strptime(s.replace("GMT", "+00:00"), "%m.%d.%Y %I:%M %p %z")
print(repr(dt))
# datetime.datetime(1986, 10, 14, 21, 15, tzinfo=datetime.timezone.utc)

s = "10.14.1986 9:15 PM GMT+02:00"
dt = datetime.strptime(
    s, "%m.%d.%Y %I:%M %p %Z%z"
)  # datetime.strptime(s, "%m.%d.%Y %I:%M %p GMT%z")
print(repr(dt))
# datetime.datetime(1986, 10, 14, 21, 15, tzinfo=datetime.timezone(datetime.timedelta(seconds=7200), 'GMT'))

# -----------------------------------------------------------------------------
# basics, datetime to string

print("the current time is", datetime.now().strftime("%I:%M %p").upper())
# the current time is 07:47 PM

# or even
print("today is", datetime.now().strftime("%A, %B %Y"))
# today is Tuesday, October 2021

print(datetime.now(timezone.utc).isoformat(timespec="milliseconds"))
# 2021-10-05T17:50:34.972+00:00
