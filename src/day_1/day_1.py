from ..prelude import *

log = setup_logger(__file__)


@attr.s(repr=False)
class Data:
    nums: List[int] = attr.ib()
    target: int = attr.ib(default=2020)

    @property
    def count(self):
        return len(self.nums)

    def __repr__(self) -> str:
        return f"<{self.count} nums, target {self.target}>"


class Day1(Problem[Data]):
    day = 1

    @classmethod
    def parse(cls, lines) -> Data:
        return Data([int(x) for x in lines])


class Part1(Day1):
    part = 1

    model = f"""
    int: N;
    set of int: INDEX = 1 .. N;
            
    array[INDEX] of int: xs;
    int: target;

    var INDEX: i;
    var INDEX: j;
    
    var int: a;
    var int: b;

    constraint a = xs[i];
    constraint b = xs[j];
    constraint a + b = target;
    solve maximize a*b;
        
    """

    @classmethod
    def formulate(cls, data: Data):
        return dict(model=cls.model, xs=data.nums, N=data.count, target=data.target)


d1p1 = Part1()


class Part2(Day1):
    part = 2

    model = f"""
    int: N;
    set of int: INDEX = 1 .. N;

    array[INDEX] of int: xs;
    int: target;

    var INDEX: i;
    var INDEX: j;
    var INDEX: k;

    var int: a;
    var int: b;
    var int: c;

    constraint a = xs[i];
    constraint b = xs[j];
    constraint c = xs[k];

    constraint a + b + c = target;
    solve maximize a*b*c;
    """

    @classmethod
    def formulate(cls, data):
        return dict(model=cls.model, xs=data.nums, N=data.count, target=data.target)


d1p2 = Part2()
