import pytest
from src import *


@pytest.fixture(params=Problem.list)
def problem(request):
    return request.param
