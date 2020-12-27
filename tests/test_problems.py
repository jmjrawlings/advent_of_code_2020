import pytest

from src.prelude import *

log = setup_logger(__name__)


def test_problem(problem: Problem):
    sol = problem.solve()
    assert sol.answer


@pytest.mark.asyncio
async def test_solve():
    opts = SolveOpts()
    model = "var 0..1: x; solve maximize x;"
    sol = await solve(model, opts)
    assert sol.status == Status.OPTIMAL_SOLUTION
    assert sol.data.x == 1


@pytest.mark.asyncio
async def test_satisfy():
    opts = SolveOpts()
    model = "var 1..1: x; solve satisfy;"
    sol = await solve(model, opts)
    assert sol.status == Status.SATISFIED
    assert sol.data.x == 1


@pytest.mark.asyncio
async def test_syntax_error():
    opts = SolveOpts()
    model = "asdf"
    with pytest.raises(Exception):
        sol = await solve(model, opts)
