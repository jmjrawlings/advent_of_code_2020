import pytest
from src import *

problems = [d1p2, d1p2, d2p1, d2p2]


@pytest.fixture(params=problems)
def problem(request):
    return request.param
