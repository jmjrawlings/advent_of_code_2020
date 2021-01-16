import pytest
from src import *


@pytest.fixture(params=Part.list)
def part(request):
    return request.param


@pytest.fixture(params=Day.list)
def day(request):
    return request.param
