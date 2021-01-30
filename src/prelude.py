import asyncio
import datetime as dt
import string
from functools import partial
from pathlib import Path
from enum import Enum
from subprocess import call
from typing import (
    Any,
    Callable,
    Dict,
    Generator,
    Generic,
    List,
    Optional,
    Tuple,
    Type,
    TypeVar,
    Union,
    get_args,
)

import attr
import pendulum as pn
from logzero import setup_logger
from minizinc import Instance, Model, Result, Solver, Status
from pendulum import (
    Date,
    DateTime,
    Duration,
    Period,
    date,
    datetime,
    duration,
    period,
)
from pendulum.tz.timezone import UTC, Timezone

log = setup_logger("app")

T = TypeVar("T")


# An argument to a function
Arg = Union[T, Type[T], Callable[[], T]]


def arg(type: Type[T], val: Arg[T]) -> T:
    """ Convert the give value to the type """

    if isinstance(val, type):
        return val
    if callable(val):
        return arg(type, val())
    if val is None:
        return type()

    raise ValueError(f"Could not unpack argument {val} as {type.__name__}")


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
        ret = f"{micros}μs"

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


def now():
    return to_datetime(pn.now())


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

    if not (args or kwargs):
        return Period(now(), now())

    if s is not None and e is not None:
        st = to_datetime(s)
        et = to_datetime(e)
        if st > et:
            raise ValueError(f"{st} > {et}")
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


log = setup_logger(__name__)


E = TypeVar("E", bound=Enum)


class Base:
    @classmethod
    def fields(cls):
        return attr.fields_dict(cls)

    def __setattr__(self, name: str, value: Any) -> None:
        """ Call attrs converts on setattribute """
        field = self.fields().get(name)
        if not field:
            return super().__setattr__(name, value)

        if field.converter:
            value = field.converter(value)

        return super().__setattr__(name, value)


class Enumeration(Enum):
    @classmethod
    def parse(cls: Type[E], x: Any) -> E:
        if isinstance(x, cls):
            return x
        try:
            return cls[x]
        except:
            return cls(x)


class Engine(Enumeration):
    CHUFFED = "chuffed"
    GECODE = "gecode"
    CBC = "cbc"


@attr.s
class SolveOpts(Base):
    """ Solving Options """

    # fmt: off
    intermediate : bool     = attr.ib(default=False)
    engine       : Engine   = attr.ib(default=Engine.GECODE, converter=Engine.parse) # type: ignore
    timeout      : Duration = attr.ib(factory=to_dur, converter=to_dur)
    processes    : int      = attr.ib(default=4)
    # fmt: on


@attr.s
class Solution(Base):

    # fmt: off
    iteration  : int             = attr.ib(default=1)
    status     : Status          = attr.ib(default=Status.UNKNOWN)
    total_time : Period          = attr.ib(factory=to_period)
    iter_time  : Period          = attr.ib(factory=to_period)
    answer     : Optional[int]   = attr.ib(default=None)
    bound      : Optional[int]   = attr.ib(default=None)
    gap        : Optional[int]   = attr.ib(default=None)
    rgap       : Optional[float] = attr.ib(default=None)
    delta      : Optional[int]   = attr.ib(default=None)
    rdelta     : Optional[float] = attr.ib(default=None)
    statistics : Dict[str,Any]   = attr.ib(factory=dict)
    data       : Dict[str, Any]  = attr.ib(factory=dict)
    # fmt: on

    def __str__(self):
        s = f"iter={self.iteration} ans={self.answer}"
        if self.bound:
            s += f" bnd={self.bound} gap={self.gap} rgap={self.rgap} del={self.delta} rdel={self.rdelta}"
        return s


async def solutions(model: str, opts: Arg[SolveOpts] = SolveOpts, name="", **kwargs):
    from math import isfinite

    model_ = Model()
    model_.add_string(model)

    opts = arg(SolveOpts, opts)
    log.info(f"solve {opts} opts")

    solver = Solver.lookup(opts.engine.value)
    instance = Instance(solver, model_)

    for k, v in kwargs.items():
        instance[k] = v

    solver_args: Dict[str, Any] = dict(intermediate_solutions=opts.intermediate)

    if opts.timeout:
        solver_args["timeout"] = opts.timeout

    if opts.processes and "-p" in solver.stdFlags:
        solver_args["processes"] = opts.processes

    i = 0
    last = Solution()
    solve_start = now()
    iter_start = solve_start

    try:
        async for result in instance.solutions(**solver_args):
            status = result.status
            objective = result.objective
            values = result.solution
            stats = result.statistics

            i += 1
            iter_end = now()
            total_time = pn.period(solve_start, iter_end)
            iter_time = pn.period(iter_start, iter_end)
            obj = objective

            sol = Solution(
                total_time=total_time,
                iter_time=iter_time,
                answer=obj,
                status=status,
                statistics=stats,
                iteration=i,
                data=values,
            )

            bound = stats.get("objectiveBound", None)
            if (bound is not None) and isfinite(bound):
                sol.bound = int(bound)
                sol.gap = abs(sol.answer - sol.bound)  # type: ignore
                sol.rgap = None if not sol.bound else (sol.gap / sol.bound)
                if last.gap is not None:
                    sol.delta = sol.gap - last.gap
                    sol.rdelta = sol.rgap - last.rgap  # type:ignore

            if not values:
                sol.data = last.data
                sol.answer = last.answer
                sol.gap = last.gap
                sol.rgap = last.rgap
                sol.bound = last.bound
                sol.delta = last.delta
                sol.rdelta = last.rdelta

            # log.error(f"{iter_time.start} {iter_time.end}")
            # log.error(f"{total_time.start} {total_time.end}")
            assert sol.total_time.start == solve_start

            log.debug(
                f"i={sol.iteration} obj={sol.answer} iter={to_elapsed(iter_time)} total={to_elapsed(total_time)}"
            )
            last = sol
            iter_start = iter_end

            yield sol

    except ProcessLookupError as e:
        pass

    log.info(f"solve {opts} fin")


async def solve(model: str, opts: Arg[SolveOpts] = SolveOpts, **kwargs):
    """ Solve the given model and return the best solution """

    sol = Solution()

    async for sol in solutions(model, opts, **kwargs):
        pass

    return sol


class Day(Generic[T]):
    """ An problem for the given Day/Part """

    num: int
    title: str
    input: str

    part_1: "Part[T]"
    part_2: "Part[T]"
    s: List["Day"] = []

    def __init__(self):
        self.log = setup_logger(self.name)

    def data(self, lines: List[str]) -> T:
        """
        Load the problem instance from the lines
        of the input file
        """
        raise NotImplementedError()

    @property
    def dir(self) -> Path:
        return root / "src" / self.name

    @property
    def name(self):
        return f"day_{self.num}"

    @property
    def lines(self):
        for line in self.input.split("\n"):
            if line:
                yield line.strip()


parts: Dict[Tuple[int, int], "Part"] = {}


class Part(Generic[T]):
    def __init__(self, day: Day[T], num: int):
        self.num = num
        self.day = day
        self.log = setup_logger(self.name)

    blurb: str
    s: List["Part"] = []

    @property
    def name(self):
        return f"day{self.day.num}_part{self.num}"

    @property
    def title(self):
        return f"{self.day.title} Part {self.num}"

    def formulate(self, data: T) -> Dict[str, Any]:
        """
        Formulate the problem as a model to solve
        """
        raise NotImplementedError()

    async def answer(self, data: T, opts: Arg[SolveOpts] = SolveOpts) -> int:
        model = self.formulate(data)
        sol = await solve(opts=opts, **model)
        return sol.answer

    async def solve(
        self, data: Optional[T] = None, opts: Arg[SolveOpts] = SolveOpts
    ) -> int:
        start_time = now()
        code = f"D{self.day.num}P{self.num}"
        log.info(f"{code} solve start")

        if data is None:
            lines = list(self.day.lines)
            data = self.day.data(lines)

        answer = await self.answer(data, opts)
        log.info(f"{code} returned {answer} in {to_elapsed(now() - start_time)}")
        return answer


def register(day: Type[Day[T]], part_1: Type[Part[T]], part_2: Type[Part[T]]):
    d = day()
    p1 = part_1(day=d, num=1)
    p2 = part_2(day=d, num=2)
    d.part_1 = p1
    d.part_2 = p2
    Day.s.append(d)
    Part.s += [p1, p2]
