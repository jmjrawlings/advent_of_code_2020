from src.day_1 import load_input
from src.prelude import *

log = setup_logger(__file__)


class Day1(Problem):
    day = 1

    def load_input(self):
        xs = [int(x) for x in self.lines]
        log.debug(f"{len(xs)} numbers read")
        return xs, len(xs)


class Part1(Day1):
    def solve():

        numbers, n = self.load_input()

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

        sol = solve_model(model, xs=numbers, target=target)
        answer = sol.a * sol.b
        log.info(f"part_1 = {answer}")
        return answer


def part_2(target=2020):

    numbers, n = load_input()

    model = f"""
    set of int: INDEX = 1 .. {n};
    
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

    sol = solve_model(model, xs=numbers, target=target)
    answer = sol.a * sol.b * sol.c
    logger.info(f"part_2 = {answer}")
    return answer