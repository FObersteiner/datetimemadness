# A 2021 tour of datetime, time zones and timedelta in Python
> ***if you don't set a time zone, it's local time!***

This article gives a quick tour of how to handle date/time, time zones and durations in Python 3.9 and higher. It should help you to avoid the common pitfalls I've encountered personally and in many questions around the subject on [stackoverflow](https://stackoverflow.com/).



### Content
- [What is "datetime"?](#what-is-datetime)
- [Give me date and time now!](#give-me-date-and-time-now)
- [From string](#from-string)
- [To string](#and-to-string)
- [Setting time zones](#setting-time-zones-and-converting-between-them)
- [UNIX time](#unix-time)
- [Durations: timedelta](#durations-timedelta)
- [Do's and Don'ts](#dos-and-donts)
- [Useful third party packages](#useful-third-party-packages)
- [About](#about)



### What is "datetime"?
In the context of this article, datetime is a data structure to hold information on date and time, based on a certain calendar. In Python, you have [class datetime](https://docs.python.org/3/library/datetime.html#datetime-objects) from the [datetime module](https://docs.python.org/3/library/datetime.html) (standard library) for that purpose. It uses the [Gregorian calendar](https://en.wikipedia.org/wiki/Gregorian_calendar) we're all used to.



### Give me date and time now!
To get the current time, you write
```Python
from datetime import datetime

now = datetime.now()
print(now) # prints the string representation of the datetime object
# 2021-10-05 19:32:04.898003
```
`now` is what you would see on your wall clock, although it probably doesn't show microseconds. 

If you inspect closer,
```Python
print(repr(now))
# datetime.datetime(2021, 10, 5, 19, 32, 4, 898003)
```
you see that the object has no time zone specified, it's just the time your operating system is configured to use. The `datetime` object is said to be [naïve](https://docs.python.org/3/library/datetime.html#aware-and-naive-objects). Computers are ubiquitous all around the world, in many different time zones - so if you'd want something "universal", you can write
```Python
from datetime import timezone

now_utc = datetime.now(timezone.utc)
print(now_utc)
# 2021-10-05 17:32:04.898176+00:00
print(repr(now_utc))
# datetime.datetime(2021, 10, 5, 17, 32, 4, 898176, tzinfo=datetime.timezone.utc)
```
But before we dive into time zones, let's discuss how you get a `datetime` object from a string of characters. And of course the other way around, how you can get a string that shows date and time in a "human-readable" way.



### From string
In Python, you **p**arse a string to a `datetime` object with the [str**p**time](https://docs.python.org/3/library/datetime.html#strftime-and-strptime-behavior) method, and you create a string that shows date/time in a certain **f**ormat with the [str**f**time](https://docs.python.org/3/library/datetime.html#strftime-and-strptime-behavior) method. To be precise with wording, only the text in a string can have a certain *format*, not the `datetime` object itself since it's a data structure.

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
# datetime.datetime(1900, 1, 1, 21, 15)
# -> note that a default date was added
```
All units of date and time have to be matched by a directive `%...` while all other characters have to be exactly as in the input. For example
```Python
s = "10.14.1986"
dt = datetime.strptime(s, "%m/%d/%Y")
```
will fail with 
> ValueError: time data '10.14.1986' does not match format '%m/%d/%Y'

because I used the wrong delimiter, `/` should be `.`

***ISO format***
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

***Pitfall: %Z vs. UTC or GMT***
There is a parsing directive `%Z` (capital letter Z) that can make `strptime` accept `"GMT"` and `"UTC"`. However, the information (this date/time is in UTC) is actually ignored:
```Python
s = "10.14.1986 9:15 PM GMT"
dt = datetime.strptime(s, "%m.%d.%Y %I:%M %p %Z")
print(repr(dt))
# datetime.datetime(1986, 10, 14, 21, 15)
print(dt.tzinfo)
# None
``` 
Notice that the `tzinfo` attribute of the datetime object is still `None`. That's bad because it means the datetime object is naive - so treated like *local time*. A work-around could be (notice the lower-case `%z`):
```Python
dt = datetime.strptime(s.replace("GMT", "+00:00"), "%m.%d.%Y %I:%M %p %z")
print(repr(dt))
# datetime.datetime(1986, 10, 14, 21, 15, tzinfo=datetime.timezone.utc)
```
`%Z`still is kind of useful if your input specifies a UTC offset. You can use a combination of `%Z%z` e.g. in
```Python
s = "10.14.1986 9:15 PM GMT+02:00"
dt = datetime.strptime(s, "%m.%d.%Y %I:%M %p %Z%z")
print(repr(dt))
# datetime.datetime(1986, 10, 14, 21, 15, tzinfo=datetime.timezone(datetime.timedelta(seconds=7200), 'GMT'))
```
A parsing directive of `"%m.%d.%Y %I:%M %p GMT%z"` would have worked as well though, the tzinfo attribute just wouldn't have a name.


### ...and to string
Same directives work the other way around. Just tell the computer what to do, e.g.
```Python
print("the current time is", datetime.now().strftime("%I:%M %p"))
# the current time is 07:47 pm

# or even
print("today is", datetime.now().strftime("%A, %B %Y"))
# today is Tuesday, October 2021
```
Convenient is also the [isoformat](https://docs.python.org/3/library/datetime.html#datetime.datetime.isoformat) method,
```Python
print(datetime.now(timezone.utc).isoformat(timespec="milliseconds"))
# 2021-10-05T17:50:34.972+00:00
```
...although this might not be considered "readable" by the typical human, computers (and programmers) will like it. See [ISO 8601](https://en.wikipedia.org/wiki/ISO_8601) and [RFC 3339](https://datatracker.ietf.org/doc/html/rfc3339) for more info.



### Setting time zones and converting between them
The intro section already shows how to set UTC. What about other time zones?

With Python version 3.9 we have [zoneinfo](https://docs.python.org/3/library/zoneinfo.html) in the standard library to handle those. Just specify a time zone name from the [IANA tz database](https://www.iana.org/time-zones) (Wikipedia has [an overview](https://en.wikipedia.org/wiki/List_of_tz_database_time_zones)):

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

We can also observe that if we convert to UTC with the [astimezone](https://docs.python.org/3/library/datetime.html#datetime.datetime.astimezone) method:
```Python
now_UTC = now_Pacific.astimezone(ZoneInfo("UTC"))
print(f"current UTC time: {now_UTC.isoformat(timespec='seconds')}")
# current UTC time: 2021-10-17T08:19:22+00:00
```
We can also convert to another time zone; observe how the time changes from 1 am to 10 am and the UTC offset is now 2 hours ahead of UTC:
```Python
now_Germany = now_Pacific.astimezone(ZoneInfo("Europe/Berlin"))
print(f"current time in Germany: {now_Germany.isoformat(timespec='seconds')}")
# current time in Germany: 2021-10-17T10:19:22+02:00
```
We came from UTC-7 to UTC+2 so the total difference between those two time zones is 9 hours.


***I have naive datetime, how can I set a certain time zone?***
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

***What about daylight saving time transitions?***
If the time zone is set, transitions of daylight saving time (DST) are handled. For example in Germany (time zone *Europe/Berlin*), we'll transition from summer- to winter time on Oct 31st 2021:
```Python
summer = datetime(2021, 10, 30, tzinfo=ZoneInfo("Europe/Berlin"))
winter = datetime(2021, 11, 1, tzinfo=ZoneInfo("Europe/Berlin"))
print(f"summer time: {summer.isoformat()}")
print(f"winter time: {winter.isoformat()}")
# summer time: 2021-10-30T00:00:00+02:00
# winter time: 2021-11-01T00:00:00+01:00
```
The UTC offset changed from +2 hours during summer time to +1 hour during winter time.


***Time zone rules change over time***
Time zone rules, e.g. when DST starts and ends, are subject to political decisions. So expect them to change. How is this being taken into account? Python's `zoneinfo` tries to use your system's tz database, that is e.g. provided and kept up-to-date by the `tzdata` package on UNIX systems. For systems that do not offer such time zone data (e.g. Windows), there is a first party Python package [tzdata](https://tzdata.readthedocs.io/en/latest/).



### UNIX time
> todo >> from Unix time to datetime and back


### Durations: timedelta
> todo >> wall time example


### Do's and Don'ts
- Better avoid [utcnow](https://docs.python.org/3/library/datetime.html#datetime.datetime.utcnow) and [utcfromtimestamp](https://docs.python.org/3/library/datetime.html#datetime.datetime.utcfromtimestamp). Why? Both return naïve datetime objects while the name clearly indicates something else - UTC! That is simply misleading in my opinion and can cause nasty, unexpected results.
- [pytz](https://pythonhosted.org/pytz/) should be considered legacy and not used anymore in new projects. There is a [deprecation shim](https://github.com/pganssle/pytz-deprecation-shim) for older projects that have to rely on this dependency for some reason. For older Python versions, there's [dateutil.tz](https://dateutil.readthedocs.io/en/stable/tz.html) which uses the same semantics as `zoneinfo` or [backports.zoneinfo](https://pypi.org/project/backports.zoneinfo/).


### Useful third party packages
- [dateutil](https://github.com/dateutil/dateutil) - powerful extension to the standard lib's `datetime`, for example with a great universal [parser](https://dateutil.readthedocs.io/en/stable/parser.html), [relativedelta](https://dateutil.readthedocs.io/en/stable/relativedelta.html) and more.
- [tzlocal](https://github.com/regebro/tzlocal) - tries to figure out what your local timezone is.
- [timezonefinder](https://github.com/jannikmi/timezonefinder) - finds the time zone at any point on earth (offline).
- [whereareyou](https://github.com/MrFuppes/whenareyou) - use Uses nominatim.openstreetmap.org to find the time zone of a given location name (e.g. a city).


### About
Why did this topic catch my interest? In our day-to-day life, date and time can be pretty weird things. Just think about how countries change daylight saving times as they see fit. Maybe convenient for the locals. But very confusing to foreign people happening to travel there! Now computers should handle this?! They're not known to be very political - more weird stuff to be expected! Find [me on stackoverflow](https://stackoverflow.com/users/10197418/mrfuppes) looking for such things.
