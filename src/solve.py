from os import stat
from struct import Struct
from .prelude import *

from minizinc import Model, Instance, Solver, Result, Status

log = setup_logger(__name__)


@attr.s
class SolveOpts:
    """ Solving Options """

    # fmt: off
    intermediate : bool      = attr.ib(default=True)
    solver       : str       = attr.ib(default="gecode")
    timeout      : Duration  = attr.ib(factory=to_dur,converter=to_dur)
    processes    : int       = attr.ib(default = 4)
    # fmt: on


@attr.s
class SolveResult:
    status: Status = attr.ib()
    solve_time: Period = attr.ib(converter=to_period)


@attr.s
class SolveError(SolveResult):
    message: str = attr.ib(default="")


@attr.s
class SolveStats(SolveResult):
    """ Solver Statistics """

    # fmt: off
    iteration  : int             = attr.ib()
    iter_time  : Period          = attr.ib(converter=to_period)
    objective  : Optional[int]   = attr.ib(default=None)
    bound      : Optional[int]   = attr.ib(default=None)
    gap        : Optional[int]   = attr.ib(default=None)
    relgap     : Optional[float] = attr.ib(default=None)
    absgap     : Optional[int]   = attr.ib(default=None)
    stats      : Dict[str,Any]   = attr.ib(factory=dict)
    # fmt: on


async def solve(model: str, opts: SolveOpts = SolveOpts(), **kwargs):
    from math import isfinite

    model_ = Model()
    model_.add_string(model)

    solver_ = Solver.lookup(opts.solver)
    instance = Instance(solver_, model_)

    for k, v in kwargs.items():
        instance[k] = v

    solver_args = dict(intermediate_solutions=opts.intermediate)

    if opts.timeout:
        solver_args["timeout"] = opts.timeout

    if opts.processes and "-p" in solver_.stdFlags:
        solver_args["processes"] = opts.processes

    i = 0
    last: Dict[Any, Any] = {}
    clock_start = now()
    iter_start = now()

    async for result in instance.solutions(**solver_args):

        res: Result = result

        i += 1

        clock_end = now()
        iter_end = now()
        clock_time = clock_end - clock_start
        iter_time = iter_end - iter_start

        objective = res.objective
        status = res.status
        bound = res.statistics.get("objectiveBound", None)
        if bound is not None and isfinite(bound):
            bound = int(bound)
            gap = objective - bound
            absgap = abs(gap)
            relgap = None if not bound else (gap / bound)
        else:
            gap, absgap, relgap = None, None, None

        stats = SolveStats(
            iteration=i,
            status=status,
            iter_time=iter_time,
            solve_time=clock_time,
            objective=objective,
            bound=bound,
            gap=gap,
            relgap=relgap,
            absgap=absgap,
        )

        log.debug(f"{i:3} {stats.status.name:20} {stats.objective!s:20}")

        solution = res.solution or {}

        if not solution:

            if res.status in [
                Status.ERROR,
                Status.UNBOUNDED,
                Status.UNSATISFIABLE,
                Status.UNKNOWN,
            ]:
                yield solution, SolveError(res.status, clock_time)

            elif res.status == Status.OPTIMAL_SOLUTION:
                yield last, stats

            continue

        yield solution, stats

        last = solution
