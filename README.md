# A 2021 tour of datetime, time zones and timedelta in Python
> ***if you don't set a time zone, it's local time!***

This article gives a quick tour of how to handle date/time, time zones and durations in Python 3.9 and higher. It should help you to avoid the common pitfalls I've encountered personally and in many questions around the subject on [stackoverflow](https://stackoverflow.com/).


### Content
- [What is "datetime"?](#what-is-datetime)
- [Give me date and time now!](#give-me-date-and-time-now)
- [From string](#from-string)
- [To string](#and-to-string)
- [Setting UTC and time zones](#setting-utc-and-time-zones)
- [Unix time](#unix-time)
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
print(now)
# prints the string representation of the datetime object, for example
# 2021-10-05 19:32:04.898003

# or with a bit of formatting:
print(f"the current time is {now.time()}, on {now.date()}")
# the current time is 19:32:04.898003, on 2021-10-05
```
`now` is what you would see on your wall clock. If you inspect closer,
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
But before we dive into time zones, let's discuss how you can get a string that shows date and time. And of course the other way around, how you get a `datetime` object from a string of characters.


### From string
In Python, you **p**arse a string to a `datetime` object with the [str**p**time](https://docs.python.org/3/library/datetime.html#strftime-and-strptime-behavior) method, and you create a string that shows date/time in a certain **f**ormat with the [str**f**time](https://docs.python.org/3/library/datetime.html#strftime-and-strptime-behavior) method. To be precise with wording, only the text in a string can have a certain *format*, not the `datetime` object itself since it's just a data structure.

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
# note that a default date was added
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
Since 3.7, Python's standard library offers to parse [ISO 8601](https://en.wikipedia.org/wiki/ISO_8601) compatible formats (although not arbitrary):
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

***pitfall: %Z vs. UTC or GMT***
There is a parsing directive `%Z` (capital letter Z) that can make strptime accept `"GMT"` and `"UTC"`. However, the information (this date/time is UTC!) is actually ignored:
```Python
s = "10.14.1986 9:15 PM GMT"
dt = datetime.strptime(s, "%m.%d.%Y %I:%M %p %Z")
print(repr(dt))
# datetime.datetime(1986, 10, 14, 21, 15)
``` 
Notice that the `tzinfo` attribute of the datetime object is still `None`! That's bad because it means the datetime object is naive - so treated like *local time*. A work-around could be (notice the lower-case `%z`):
```Python
dt = datetime.strptime(s.replace("GMT", "+00:00"), "%m.%d.%Y %I:%M %p %z")
print(repr(dt))
# datetime.datetime(1986, 10, 14, 21, 15, tzinfo=datetime.timezone.utc)
```

### ...and to string
Same directives work the other way around, e.g.
```Python
print("the current time is", datetime.now().strftime("%I:%M %p").upper())
# the current time is 07:47 PM

# or even
print(datetime.now().strftime("today is %A, %B %Y"))
# today is Tuesday, October 2021
```
Convenient is also [isoformat](https://docs.python.org/3/library/datetime.html#datetime.datetime.isoformat),
```Python
print(datetime.now(timezone.utc).isoformat(timespec="milliseconds"))
# 2021-10-05T17:50:34.972+00:00
```
...although this might not be considered "readable" by the typical human, computers (and programmers) will like it. See [ISO 8601](https://en.wikipedia.org/wiki/ISO_8601) and [RFC 3339](https://datatracker.ietf.org/doc/html/rfc3339) for more info.




### Setting UTC and time zones
The intro section already shows how to set UTC. What about other time zones?

zoneinfo example

time zone definitions change over time - how is the tz database kept up-to-date?


### Unix time
from Unix time to datetime and back


### Durations: timedelta
wall time example


### Do's and Don'ts
- Better avoid [utcnow](https://docs.python.org/3/library/datetime.html#datetime.datetime.utcnow) and [utcfromtimestamp](https://docs.python.org/3/library/datetime.html#datetime.datetime.utcfromtimestamp). Why? Both return naïve datetime objects while the name clearly indicates something else (UTC!). That is simply misleading in my opinion and can cause nasty, unexpected results.
- [pytz](https://pythonhosted.org/pytz/) should be considered legacy and not used anymore in new projects. There is a [deprecation shim](https://github.com/pganssle/pytz-deprecation-shim) for older projects that have to rely on this dependency for some reason.


### Useful third party packages
- dateutil
- tzlocal
- timezonefinder
- whereareyou


### About
Why did this topic catch my interest? In our day-to-day life, date and time can be pretty weird things. Just think about how countries change daylight saving times as they see fit. Maybe convenient for the locals. But very confusing to foreign people happening to travel there! Now computers should handle this?! They're not known to be very political - more weird stuff to be expected! Find [me on stackoverflow](https://stackoverflow.com/users/10197418/mrfuppes) looking for such things.
