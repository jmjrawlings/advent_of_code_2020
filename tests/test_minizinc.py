import pytest
from src import *


@pytest.mark.asyncio
async def test_solve():
    opts = SolveOpts()
    model = "var 0..1: x; solve maximize x;"
    sol = await solve(model, opts)
    assert sol.status == Status.OPTIMAL_SOLUTION
    assert sol.data.x == 1


@pytest.mark.asyncio
async def test_syntax_error():
    opts = SolveOpts()
    model = "asdf"
    with pytest.raises(Exception):
        sol = await solve(model, opts)
