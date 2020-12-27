import asyncio
import datetime as dt
import string
from abc import ABC, abstractmethod
from functools import partial
from pathlib import Path
from typing import (
    Any,
    Callable,
    Dict,
    Generator,
    Generic,
    List,
    Optional,
    Type,
    TypeVar,
    Union,
)

import attr
import pendulum as pn
from logzero import setup_logger
from pendulum import (
    Date,
    DateTime,
    Duration,
    Period,
    date,
    datetime,
    duration,
    now,
    period,
)
from pendulum.tz.timezone import UTC, Timezone

log = setup_logger("app")

T = TypeVar("T")


def to_dur(*args, **kwargs) -> Duration:
    """ Create a Duration from the given arguments """

    if not args:
        if kwargs:
            return duration(**kwargs)
        else:
            return duration()

    arg = args[0]

    if isinstance(arg, Period):
        return arg.as_interval()

    elif isinstance(arg, Duration):
        return arg

    elif isinstance(arg, dt.timedelta):
        return duration(seconds=arg.total_seconds())

    elif not arg:
        return duration()

    else:
        raise ValueError(f"Cannot make duration from {args} and {kwargs}")


def fmt_int(n: int, single, multi, none="") -> str:
    """ Format int """
    if n == 0:
        return none
    elif n == 1:
        return f"{1}{single}"
    else:
        return f"{n}{multi}"


fmt_day = partial(fmt_int, single="d", multi="d")
fmt_hr = partial(fmt_int, single="h", multi="h")
fmt_min = partial(fmt_int, single="m", multi="m")
fmt_sec = partial(fmt_int, single="s", multi="s")


def to_elapsed(obj: Any) -> str:
    """ Convert to an elapsed string """

    dur = to_dur(obj)

    days = dur.days
    hr = dur.hours % 24
    mins = dur.minutes % 60
    secs = dur.seconds % 60
    millis, micros = divmod(dur.microseconds, 1000)

    ret = ""

    if days:
        ret = f"{fmt_day(days)} {fmt_hr(hr)}"

    elif hr:
        ret = f"{fmt_hr(hr)} {fmt_min(mins)}"

    elif mins:
        ret = f"{fmt_min(mins)} {fmt_sec(secs)}"

    elif secs:
        ret = f"{secs}.{millis}s"

    elif millis:
        ret = f"{millis}ms"

    elif micros:
        ret = f"{millis}μs"

    else:
        ret = "0s"

    # log.debug(f'{dur} -> {ret}')
    return ret


def to_datetime(value, tz=UTC, warn_on_convert=True) -> DateTime:
    """ Convert the given value to a DateTime if possible """

    if isinstance(value, DateTime):
        val = value

    elif isinstance(value, dt.datetime):
        val = pn.instance(value)

    elif isinstance(value, dt.date):
        val = pn.datetime(year=value.year, month=value.month, day=value.day)

    elif isinstance(value, str):
        parsed = pn.parse(value, tz=tz)
        return to_datetime(parsed, tz, warn_on_convert)

    else:
        raise ValueError(f"Could not convert {value} to datetime")

    ret = val.in_tz(tz)

    if not val.tz or (val.offset_hours != ret.offset_hours):
        if warn_on_convert:
            log.warning(f"{val} in tz {val.tz} was localized to {tz.name} as {ret}")

    return ret


def to_date(value) -> Date:
    """ Convert the given value to a Date """

    if isinstance(value, Date):
        return value

    elif isinstance(value, dt.date):
        return date(value.year, value.month, value.day)

    else:
        return to_datetime(value).date()


def to_period(*args, **kwargs) -> Period:
    """ Convert the given arguments to a Period """

    n = len(args)
    s = kwargs.pop("start") if "start" in kwargs else None
    e = kwargs.pop("end") if "end" in kwargs else None
    d = kwargs.get("duration") if "duration" in kwargs else None

    if s is not None and e is not None:
        st = to_datetime(s)
        et = to_datetime(e)
        return Period(st, et, absolute=True)

    if s is not None and d is not None:
        st = to_datetime(s)
        dur = to_dur(d)
        return Period(st, st + dur, absolute=True)

    if n == 2:
        if isinstance(args[1], Duration):
            return to_period(start=args[0], duration=args[1])
        else:
            return to_period(start=args[0], end=args[1])

    if n == 1:
        arg = args[0]
        if isinstance(arg, Period):
            return to_period(start=arg.start, end=arg.end)
        elif hasattr(arg, "period"):
            if callable(arg.period):
                return arg.period()
            else:
                return arg.period
        else:
            st = to_datetime(arg)
            duration = d or to_dur(**kwargs)
            et = st + duration
            return to_period(start=st, end=et)

    raise ValueError(f"Could not convert {args} {kwargs} to Period")


def to_mins(x) -> float:
    return to_dur(x).total_seconds() / 60


def to_mid(x) -> DateTime:
    p = to_period(x)
    return p.start.add(seconds=p.total_seconds() / 2)


def opt(f: Callable[..., T]) -> Callable[..., Optional[T]]:
    def inner(arg):
        if arg is None:
            return None
        else:
            return f(arg)

    return inner


root = Path(__file__).parent.parent


class Problem(ABC, Generic[T]):
    """ An problem for the given Day/Part """

    day = 0
    part = 0

    @classmethod
    @abstractmethod
    def load_data(cls, lines: List[str]) -> T:
        """
        Load the problem instance from the lines
        of the input file
        """
        pass

    @classmethod
    @abstractmethod
    async def solve_data(cls, data: T):
        """
        Solve the problem instance given
        the input data
        """
        pass

    @classmethod
    def solve(cls: "Type[Problem[T]]"):
        log.info(f"{cls.name()} started")
        start_time = now()

        lines = list(cls.read_lines())
        data = cls.load_data(lines)

        log.info(f"{cls.name()} loaded {data!r} in {to_elapsed(now() - start_time)}")

        answer = asyncio.run(cls.solve_data(data))

        log.info(f"{cls.name()} returned {answer} in {to_elapsed(now() - start_time)}")

        return answer

    @classmethod
    def day_name(cls):
        return f"day_{cls.day}"

    @classmethod
    def part_name(cls):
        return f"part_{cls.part}"

    @classmethod
    def name(cls):
        return f"{cls.day_name()}_{cls.part_name()}"

    @classmethod
    def dir(cls) -> Path:
        return root / "src" / cls.day_name()

    @classmethod
    def input_file(cls) -> Path:
        return cls.dir() / "input.txt"

    @classmethod
    def read_lines(cls):
        with cls.input_file().open("r") as src:
            for line in src.read().split("\n"):
                yield line

    def __str__(self):
        return self.name

    def __repr__(self):
        return f"<{self!s}>"
