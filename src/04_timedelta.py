#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from datetime import datetime, timedelta

duration = timedelta(hours=1, minutes=30)
print(duration)
# 1:30:00

print(duration.total_seconds())
# 5400.0

duration = datetime(2020, 1, 1, 15) - datetime(2020, 1, 1, 14)
print(duration, duration.total_seconds())
# 1:00:00 3600.0

now = datetime.now().replace(microsecond=0)  # remove microseconds for clarity
now_normalized = datetime.combine(now.date(), now.time().min)  # floor the time

sod = (now - now_normalized).total_seconds()
print(now)
# 2021-10-17 14:05:15
print(f"seconds passed since {now_normalized}: {sod}")
# seconds passed since 2021-10-17 00:00:00: 50715.0
# check the hours: print(50715//3600) --> 14

dt = datetime(2021, 10, 17) + timedelta(seconds=sod)
print(dt)
# 2021-10-17 14:05:15


from zoneinfo import ZoneInfo  # noqa

summer = datetime(2021, 10, 30, tzinfo=ZoneInfo("Europe/Berlin"))
winter = datetime(2021, 11, 1, tzinfo=ZoneInfo("Europe/Berlin"))

print(winter - summer)
# 2 days, 0:00:00

UTC = ZoneInfo("UTC")
utc_summer, utc_winter = summer.astimezone(UTC), winter.astimezone(UTC)
print(utc_winter - utc_summer)
# 2 days, 1:00:00


# --- from timedelta to string ---
def strftimedelta(td: timedelta) -> str:
    """
    strftimedelta converts a timedelta object to string in HH:MM:SS format,
    negative timedeltas will be prefixed with a minus, '-'.
    microseconds are ignored
    """
    total = td.total_seconds()
    prefix, total = ("-", total * -1) if total < 0 else ("", total)
    h, r = divmod(total, 3600)
    m, s = divmod(r, 60)
    return f"{prefix}{int(h):02d}:{int(m):02d}:{int(s):02d}"


for td in timedelta(1), timedelta(-1), timedelta(days=1.5, microseconds=500):
    print(strftimedelta(td))
# 24:00:00
# -24:00:00
# 36:00:00 # microseconds ignored


# --- from string to timedelta ---
def strptimedelta(tdstr: str) -> timedelta:
    """
    strftimedelta parses a timedelta string to a timedelta object.
    input format is [+- days](HH:MM:SS)[.f]
    """
    parts = tdstr.strip(" ").split(" ")
    d = 0 if len(parts) == 1 else int(parts[0])  # days specified?
    if len(parts) > 1:  # we have days specified
        d = int(parts[0])
    s = sum(x * y for x, y in zip(map(float, parts[-1].split(":")), (3600, 60, 1)))
    return timedelta(seconds=(s + d * 86400))


for td in timedelta(1), timedelta(-1), timedelta(days=1.5, microseconds=500):
    # output must match input
    print(f"input: {str(td)} -> output {strptimedelta(str(td))}")
# input: 1 day, 0:00:00 -> output 1 day, 0:00:00
# input: -1 day, 0:00:00 -> output -1 day, 0:00:00
# input: 1 day, 12:00:00.000500 -> output 1 day, 12:00:00.000500
