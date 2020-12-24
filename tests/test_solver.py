import pytest
from src import *


@pytest.mark.watch
@pytest.mark.asyncio
async def test_solve():
    opts = SolveOpts()
    model = "var 0..1: x; solve maximize x;"
    async for sol, stats in solve(model, opts):
        pass

    assert stats.status == Status.OPTIMAL_SOLUTION
    assert sol.x == 1
