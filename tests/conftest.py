import pytest
from src import *


@pytest.fixture(params=Problem.map.values())
def problem(request):
    return request.param
