import pytest
from src import *


@pytest.fixture(params=Part.s, ids=[p.name for p in Part.s])
def part(request):
    return request.param


@pytest.fixture(params=Day.s, ids=[d.name for d in Day.s])
def day(request):
    return request.param
