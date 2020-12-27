import pytest

from src.prelude import *

log = setup_logger(__name__)


def test_d1_p1():
    from src.day_1 import Part1

    Part1.solve()


def test_d1_p2():
    from src.day_1 import Part2

    Part2.solve()


def test_d2_p1():
    from src.day_2 import Part1

    Part1.solve()


def test_d2_p2():
    from src.day_2 import Part2

    Part2.solve()
