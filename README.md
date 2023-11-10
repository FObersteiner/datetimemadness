# A tour of datetime, time zones and timedelta in Python

> **_if you don't set a time zone, it's local time!_**

This manuscript gives a tour of how to handle date/time, time zones and durations in "vanilla" Python. It's focused on Python version 3.9 and higher.

### Overview

- [What is "datetime"?](#what-is-datetime)
- [Give me date and time now!](#give-me-date-and-time-now)
- [From string](#from-string)
- [To string](#and-to-string)
- [Time zones](#setting-time-zones-and-converting-between-them)
- [UNIX time](#unix-time)
- [Durations: timedelta](#durations-timedelta)
- [Do's and Dont's](#dos-and-donts)
- [Useful third party packages etc.](#useful-packages-etc)
- [About](#about)

---

### What is "datetime"?

In the context of this manuscript, datetime is a data structure to hold information on date and time, based on a certain calendar. In Python, you have `class` [datetime](https://docs.python.org/3/library/datetime.html#datetime-objects) from the [datetime module](https://docs.python.org/3/library/datetime.html) (standard library) for that purpose. It uses the [Gregorian calendar](https://en.wikipedia.org/wiki/Gregorian_calendar)

---

### Give me date and time now!

To get the current time, you write

```Python
from datetime import datetime

now = datetime.now()
print(now) # prints the string representation of the datetime object
# 2021-10-05 19:32:04.898003
```

`now` is what you would see on your "wall clock" (i.e. your computer's clock display), although that one probably doesn't show microseconds.

If you inspect closer,

```Python
print(repr(now))
# datetime.datetime(2021, 10, 5, 19, 32, 4, 898003)
```

you see that it's just the time your operating system is configured to use, without saying anything about the time zone. The `datetime` object is said to be [naïve](https://docs.python.org/3/library/datetime.html#aware-and-naive-objects). Computers are ubiquitous all around the world, in many different time zones - so if you'd want something "universal", you can write

```Python
from datetime import timezone

now_utc = datetime.now(timezone.utc)
print(now_utc)
# 2021-10-05 17:32:04.898176+00:00
print(repr(now_utc))
# datetime.datetime(2021, 10, 5, 17, 32, 4, 898176, tzinfo=datetime.timezone.utc)
```

Now you have _Coordinated Universal Time_ or [UTC](https://en.wikipedia.org/wiki/Coordinated_Universal_Time), as the `tzinfo` attribute tells (`tzinfo=datetime.timezone.utc`). But before we dive into time zones, let's discuss how you get a `datetime` object from a string of characters. And of course the other way around, how you can get a string that shows date and time in a certain format.

---

### From string

It is pretty common to store date/time as a string. In Python, you **p**arse a string to a datetime object with the [str**p**time](https://docs.python.org/3/library/datetime.html#strftime-and-strptime-behavior) method, and you create a string that shows date/time in a certain **f**ormat with the [str**f**time](https://docs.python.org/3/library/datetime.html#strftime-and-strptime-behavior) method. To be precise with wording, only the text in a string can have a certain _format_, not the datetime object itself since it's a data structure.

To get a string converted to datetime, just tell the computer what to do by selecting from [strftime() and strptime() Format Codes](https://docs.python.org/3/library/datetime.html#strftime-and-strptime-format-codes):

```Python
s = "10/14/1986 18:00"
dt = datetime.strptime(s, "%m/%d/%Y %H:%M")
print(repr(dt))
# datetime.datetime(1986, 10, 14, 18, 0)

# or another one, just time in AM/PM format:
s = "9:15 PM"
dt = datetime.strptime(s, "%I:%M %p")
print(repr(dt))
# datetime.datetime(1900, 1, 1, 21, 15) # -> note that a default date was added
```

All units of date and time have to be matched by a directive `%...` while all other characters have to be exactly as in the input. For example

```Python
s = "10.14.1986"
dt = datetime.strptime(s, "%m/%d/%Y")
```

will fail with

> ValueError: time data '10.14.1986' does not match format '%m/%d/%Y'

because I used the wrong delimiter, `/` should be `.`

**_ISO format_**
Since version 3.7, Python's standard library offers to parse [ISO 8601](https://en.wikipedia.org/wiki/ISO_8601) compatible formats (although not arbitrary):

```Python
s = "2020-07-30T13:17:00.333+03:00"
dt = datetime.fromisoformat(s)
print(repr(dt))
# datetime.datetime(2020, 7, 30, 13, 17, 0, 333000, tzinfo=datetime.timezone(datetime.timedelta(seconds=10800)))

# UTC offset of zero hours is parsed to UTC:
s = "1970-01-01T12:18:00+00:00"
dt = datetime.fromisoformat(s)
print(repr(dt))
# datetime.datetime(1970, 1, 1, 12, 18, tzinfo=datetime.timezone.utc)
```

**_What about 'Z' for UTC?_**
Python's `fromisoformat` doesn't seem to like that so far, but there is [a work-around](https://stackoverflow.com/a/62769371/10197418):

```Python
s = "2008-09-03T20:56:35.450686Z"
datetime.fromisoformat(s.replace('Z', '+00:00'))
# datetime.datetime(2008, 9, 3, 20, 56, 35, 450686, tzinfo=datetime.timezone.utc)
```

or just use `strptime` with the `%z` directive; `datetime.strptime(s, '%Y-%m-%dT%H:%M:%S.%f%z')`.

**_Pitfall: %Z vs. UTC/GMT_**

There is a parsing directive `%Z` (capital letter Z) that can make `strptime` accept `"GMT"` and `"UTC"`. However, the information ("this date/time is in UTC") is actually ignored:

```Python
s = "10.14.1986 9:15 PM GMT"
dt = datetime.strptime(s, "%m.%d.%Y %I:%M %p %Z")
print(repr(dt))
# datetime.datetime(1986, 10, 14, 21, 15)
print(dt.tzinfo)
# None
```

Notice that the `tzinfo` attribute of the datetime object is still `None`. That's bad because it means the datetime object is naïve - so treated like _local time_. A work-around could be (notice the lower-case `%z`):

```Python
dt = datetime.strptime(s.replace("GMT", "+00:00"), "%m.%d.%Y %I:%M %p %z")
print(repr(dt))
# datetime.datetime(1986, 10, 14, 21, 15, tzinfo=datetime.timezone.utc)
```

`%Z` still is kind of useful if your input specifies a UTC offset. You can use a combination of `%Z%z` e.g. in

```Python
s = "10.14.1986 9:15 PM GMT+02:00"
dt = datetime.strptime(s, "%m.%d.%Y %I:%M %p %Z%z")
print(repr(dt))
# datetime.datetime(1986, 10, 14, 21, 15, tzinfo=datetime.timezone(datetime.timedelta(seconds=7200), 'GMT'))
```

A parsing directive of `"%m.%d.%Y %I:%M %p GMT%z"` would have worked as well though, the `tzinfo` attribute just wouldn't have a name then.

---

### ...and to string

Same directives work the other way around. Just tell the computer exactly what to do, e.g.

```Python
print("the current time is", datetime.now().strftime("%I:%M %p"))
# the current time is 07:47 pm

# or even
print("today is", datetime.now().strftime("%A, %B %Y"))
# today is Tuesday, October 2021
```

The [isoformat](https://docs.python.org/3/library/datetime.html#datetime.datetime.isoformat) method is also convenient,

```Python
print(datetime.now(timezone.utc).isoformat(timespec="milliseconds"))
# 2021-10-05T17:50:34.972+00:00
```

...although this might not be considered "readable" by the typical human, computers (and programmers) will like it. See [ISO 8601](https://en.wikipedia.org/wiki/ISO_8601) and [RFC 3339](https://datatracker.ietf.org/doc/html/rfc3339) for more info.

---

### Setting time zones and converting between them

The intro section already shows how to set UTC. What about other time zones?

Python version 3.9 has [zoneinfo](https://docs.python.org/3/library/zoneinfo.html) in the standard library to handle those. Just specify a time zone name from the [IANA tz database](https://www.iana.org/time-zones) (Wikipedia has [an overview](https://en.wikipedia.org/wiki/List_of_tz_database_time_zones)):

```Python
from datetime import datetime
from zoneinfo import ZoneInfo

now_Pacific = datetime.now(ZoneInfo('America/Los_Angeles')) # let's assume we're in LA
print(f"current Pacific time: {now_Pacific.isoformat(timespec='seconds')}")
# current Pacific time: 2021-10-17T01:19:22-07:00
```

Printing the `tzinfo` attribute and the UTC offset shows

```Python
print(now_Pacific.tzinfo, now_Pacific.utcoffset())
# America/Los_Angeles -1 day, 17:00:00
```

the "-1 day, 17:00:00" is kind of cryptic but can be resolved as `-1 day = -24 hours`, `17:00:00 = +17 hours`, so `-7 hours` in sum. LA was 7 hours behind UTC on Oct 17th 2021.

We also observe that if we convert to UTC with the [astimezone](https://docs.python.org/3/library/datetime.html#datetime.datetime.astimezone) method:

```Python
now_UTC = now_Pacific.astimezone(ZoneInfo("UTC"))
print(f"current UTC time: {now_UTC.isoformat(timespec='seconds')}")
# current UTC time: 2021-10-17T08:19:22+00:00
```

Furthermore, we can convert to another time zone; observe how the time changes from 1 am to 10 am and the UTC offset is now 2 hours ahead of UTC:

```Python
now_Germany = now_Pacific.astimezone(ZoneInfo("Europe/Berlin"))
print(f"current time in Germany: {now_Germany.isoformat(timespec='seconds')}")
# current time in Germany: 2021-10-17T10:19:22+02:00
```

We came from UTC-7 to UTC+2 so the total difference between those two time zones is 9 hours.

**_I have naïve datetime, how can I set a certain time zone?_**

With zoneinfo's timezone objects, you can easily do that by [replacing](https://docs.python.org/3/library/datetime.html#datetime.datetime.replace) the tzinfo attribute:

```Python
naive = datetime(2021, 10, 17) # this should be in time zone Europe/Berlin...
print(naive)
# 2021-10-17 00:00:00

aware = naive.replace(tzinfo=ZoneInfo("Europe/Berlin"))
print(aware)
# 2021-10-17 00:00:00+02:00
```

Of course you can also create a datetime object with tzinfo specified:

```Python
aware = datetime(2021, 10, 17, tzinfo=ZoneInfo("Europe/Berlin"))
print(aware)
# 2021-10-17 00:00:00+02:00
```

**_What about daylight saving time transitions?_**

If the time zone is set, transitions of daylight saving time (DST) are handled. For example in Germany (time zone _Europe/Berlin_), we'll transition from summer- to winter time on Oct 31st 2021:

```Python
summer = datetime(2021, 10, 30, tzinfo=ZoneInfo("Europe/Berlin"))
winter = datetime(2021, 11, 1, tzinfo=ZoneInfo("Europe/Berlin"))
print(f"summer time: {summer.isoformat()}")
print(f"winter time: {winter.isoformat()}")
# summer time: 2021-10-30T00:00:00+02:00
# winter time: 2021-11-01T00:00:00+01:00
```

The UTC offset changed from +2 hours during summer time to +1 hour during winter time.

**_Time zone rules change over time_**

Time zone rules, e.g. when DST starts and ends, are subject to political decisions. So expect them to change. How is this being taken into account? Python's `zoneinfo` tries to use your system's tz database, that is e.g. provided and kept up-to-date by the `tzdata` package on UNIX systems. For systems that do not offer such time zone data (e.g. Windows), there is a first party Python package [tzdata](https://tzdata.readthedocs.io/en/latest/).

---

### UNIX time

[Unix time](https://en.wikipedia.org/wiki/Unix_time), i.e. units of time passed since the UNIX epoch 1970-01-01 can be a very useful means to represent date and time: it is "just a number", no complicated data structure needed. Python handles it as a floating point number that represents _seconds_ since the epoch by default. If you have any other unit as input (e.g. milliseconds), convert to seconds first. You can obtain it for a datetime object by the [timestamp](https://docs.python.org/3/library/datetime.html#datetime.datetime.timestamp) method:

```Python
from datetime import datetime, timezone

now_utc = datetime.now(timezone.utc)
print(now_utc)
# 2021-10-17 09:40:47.170662+00:00

unix = now_utc.timestamp()
print(unix)
# 1634463647.170662
```

Vice versa, [fromtimestamp](https://docs.python.org/3/library/datetime.html#datetime.datetime.fromtimestamp) does the opposite:

```Python
back_utc = datetime.fromtimestamp(unix, tz=timezone.utc)
print(back_utc)
# 2021-10-17 09:40:47.170662+00:00
```

**_What about... "if you don't set a time zone, it's local time!"_**

In the `fromtimestamp` example, I deliberately set the tz argument of the method to `timezone.utc`. What happens if we omit that?

```Python
back = datetime.fromtimestamp(unix)
print(back)
# 2021-10-17 11:40:47.170662
```

We get a time that is 2 hours ahead and the UTC offset disappeared. +2 hours is my current local time's UTC offset. If we don't set a time zone, Python gives us local time as a naïve datetime object. That can be very confusing if you expect for example UTC as the default as it is in other programming languages (and even Python packages such as [pandas](https://pandas.pydata.org/)...).

Same goes the other way 'round,

```Python
naive = datetime(2021, 10, 17)
print(naive)
# 2021-10-17 00:00:00
unix = naive.timestamp()
print(datetime.fromtimestamp(unix, timezone.utc))
# 2021-10-16 22:00:00+00:00
```

Since the Unix epoch refers to UTC, we see the local time's UTC offset appear if we convert the timestamp to an aware datetime object in UTC. To calculate the timestamp, Python in principle converts given naïve datetime to UTC, then calculates seconds since the epoch. In general, my advice would be to work with aware datetime here if you can (UTC preferred), otherwise _exclusively_ work with naïve datetime, never mix the two (as I did in the example...).

---

### Durations: timedelta

In Python, the data structure to represent durations are [timedelta objects](https://docs.python.org/3/library/datetime.html#timedelta-objects) from the `datetime` library. You can create such an object by

```Python
from datetime import timedelta
# set individual attributes:
duration = timedelta(hours=1, minutes=30)
print(duration)
# 1:30:00
```

To get the total duration in seconds as a floating point number you have a very useful method [total_seconds](https://docs.python.org/3/library/datetime.html#datetime.timedelta.total_seconds):

```Python
print(duration.total_seconds())
# 5400.0
```

`timedelta` is also returned if you subtract two datetime objects from one another:

```Python
from datetime import datetime

duration = datetime(2020, 1, 1, 15) - datetime(2020, 1, 1, 14)
print(duration, duration.total_seconds())
# 1:00:00 3600.0
```

You can use that for example to calculate how many seconds of the day have passed:

```Python
now = datetime.now().replace(microsecond=0) # remove microseconds for clarity
now_normalized = datetime.combine(now.date(), now.time().min) # floor the time

sod = (now - now_normalized).total_seconds()
print(now)
# 2021-10-17 14:05:15
print(f"seconds passed since {now_normalized}: {sod}")
# seconds passed since 2021-10-17 00:00:00: 50715.0
```

or convert seconds of day into a datetime object:

```Python
dt = datetime(2021, 10, 17) + timedelta(seconds=sod)
print(dt)
# 2021-10-17 14:05:15
```

**_timedelta and wall time_**

Remember from the time zone section, there is a DST transition from summer to winter time between those dates:

```Python
from zoneinfo import ZoneInfo

summer = datetime(2021, 10, 30, tzinfo=ZoneInfo("Europe/Berlin"))
winter = datetime(2021, 11, 1, tzinfo=ZoneInfo("Europe/Berlin"))
```

So in our physical reality, 2 days and one extra hour have passed in-between those dates. But if we look at the timedelta,

```Python
print(winter-summer)
# 2 days, 0:00:00
```

it shows us the difference that our wall clock would show us. The wall clock is of course _adjusted_ to the DST transition, i.e. turned backwards one hour in this case. If we convert both datetime objects to UTC, the "lost" hour re-appears, since UTC has no DST:

```Python
UTC = ZoneInfo("UTC")
utc_summer, utc_winter = summer.astimezone(UTC), winter.astimezone(UTC)
print(utc_winter-utc_summer)
# 2 days, 1:00:00
```

**_Limits_**

Unfortunately, there's no `strptime` or `strftime` methods that return timedelta objects, so if you want to convert to and from string, you'll have to come up with something by yourself. I've created an [example for each direction here](https://github.com/MrFuppes/pydatetimetut/blob/main/src/04_timedelta.py).

A "normal" day has 24 hours, a "normal" week has 7 days - but what about months? It could have 28 to 31 days, so a month is an ambiguous quantity. You can't represent it as a `timedelta` object. But there's dateutil's [relativedelta](https://dateutil.readthedocs.io/en/stable/relativedelta.html) in case you want to go beyond a week's duration.

---

### Dos and Don'ts

- Better avoid [utcnow](https://docs.python.org/3/library/datetime.html#datetime.datetime.utcnow) and [utcfromtimestamp](https://docs.python.org/3/library/datetime.html#datetime.datetime.utcfromtimestamp). Why? Both return naïve datetime objects while the name clearly indicates something else - UTC! That is simply misleading in my opinion and can cause nasty, unexpected results.
- [pytz](https://pythonhosted.org/pytz/) can be considered legacy and not should not be used anymore in new projects. There is a [deprecation shim](https://github.com/pganssle/pytz-deprecation-shim) for older projects that have to rely on this dependency for some reason. For older Python versions, there's [dateutil.tz](https://dateutil.readthedocs.io/en/stable/tz.html) which uses the same semantics as `zoneinfo` or [backports.zoneinfo](https://pypi.org/project/backports.zoneinfo/).

---

### Useful packages etc.

- [dateutil](https://github.com/dateutil/dateutil) - powerful extension to the standard lib's `datetime`, for example with a great universal [parser](https://dateutil.readthedocs.io/en/stable/parser.html), [relativedelta](https://dateutil.readthedocs.io/en/stable/relativedelta.html) and more.
- [tzlocal](https://github.com/regebro/tzlocal) - tries to figure out what your local time zone is.
- [timezonefinder](https://github.com/jannikmi/timezonefinder) - finds the time zone at any point on earth (offline).
- [eggert/tz](https://github.com/eggert/tz) - Paul Eggert's time zone database, if you want to dive into time zone rules.
- [whereareyou](https://github.com/MrFuppes/whenareyou) - use [nominatim.openstreetmap.org](https://nominatim.openstreetmap.org/ui/search.html) to find the time zone of a given location name (e.g. a city).

---

### About

Why did this topic catch my interest? In our day-to-day life, date and time can be pretty weird things. Just think about how countries change daylight saving times as they see fit. Maybe convenient for the locals. But very confusing to foreign people happening to travel there! Now computers should handle this?! They're not known to be very political - more weird stuff to be expected! Find [me on stackoverflow](https://stackoverflow.com/users/10197418/mrfuppes) looking for such things.
