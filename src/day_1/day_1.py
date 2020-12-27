from src import *

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
    def load_data(cls, lines) -> Data:
        return Data([int(x) for x in lines])


class Part1(Day1):
    part = 1

    @classmethod
    async def solve_data(cls, data: Data):

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

        """

        sol, stats = await solve(model, xs=data.nums, N=data.count, target=data.target)
        answer = sol.a * sol.b
        return answer


class Part2(Day1):
    part = 2

    @classmethod
    async def solve_data(cls, data: Data, target=2020):
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
        """
        sol, stats = await solve(model, xs=data.nums, N=data.count, target=data.target)
        answer = sol.a * sol.b * sol.c
        return answer
