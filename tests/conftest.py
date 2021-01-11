import pytest
from src import *


@pytest.fixture(params=Part.list)
@pytest.mark.asyncio
async def test_part(request):
    part: Part = request.param
    sol = await solve(part)
    assert sol
