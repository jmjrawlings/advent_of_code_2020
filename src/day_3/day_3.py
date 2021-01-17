from ..prelude import *


@attr.s(auto_attribs=True)
class Data:
    map: List[List[int]]
    x: int
    y: int

    def __str__(self) -> str:
        return f"<x={self.x} y={self.y}>"


class Day3(Day[Data]):
    num = 3
    title = "Toboggan Trajectory"

    def data(self, lines):

        map = []
        for line in lines:
            row = [int(x == "#") for x in line]
            map.append(row)

        y = len(map)
        x = len(lines[0])
        map = map
        return Data(map, x, y)

    model = r"""

        int: x0 = 1;
        int: y0 = 1;
        int: x1;
        int: y1;

        set of int: Y = y0 .. y1;
        set of int: X = x0 .. x1;

        int: dx;
        int: dy;

        set of int: MOVES = 1 .. (y1-1);
        var MOVES: max_move;

        array[Y, X] of 0..1: map;
        array[MOVES] of var 0..1: route;

        constraint forall (i in MOVES) (
            (i <= max_move) ->
            let {
                X: x = x0 + ((i*dx) mod x1);
                Y: y = y0 + i*dy;

                }
            in
                route[i] = map[y,x]
        );

        var int: answer;

        constraint answer = sum(route);
        solve maximize max_move;

        """

    def formulate(self, data: Data):
        return dict(model=self.model, map=data.map, dx=data.x, dy=data.y)

    def solve(self, dx, dy):
        return solve_model(self.model, y1=self.y, x1=self.x, map=self.map, dx=dx, dy=dy)


class Part1(Part[Data]):

    blurb = """
    With the toboggan login problems resolved, you set off toward the airport. While travel by toboggan might be easy, it's certainly not safe: there's very minimal steering and the area is covered in trees. You'll need to see which angles will take you near the fewest trees.

    Due to the local geology, trees in this area only grow on exact integer coordinates in a grid. You make a map (your puzzle input) of the open squares (.) and trees (#) you can see. For example:

    ..##.......
    #...#...#..
    .#....#..#.
    ..#.#...#.#
    .#...##..#.
    ..#.##.....
    .#.#.#....#
    .#........#
    #.##...#...
    #...##....#
    .#..#...#.#

    These aren't the only trees, though; due to something you read about once involving arboreal genetics and biome stability, the same pattern repeats to the right many times:

    ..##.........##.........##.........##.........##.........##.......  --->
    #...#...#..#...#...#..#...#...#..#...#...#..#...#...#..#...#...#..
    .#....#..#..#....#..#..#....#..#..#....#..#..#....#..#..#....#..#.
    ..#.#...#.#..#.#...#.#..#.#...#.#..#.#...#.#..#.#...#.#..#.#...#.#
    .#...##..#..#...##..#..#...##..#..#...##..#..#...##..#..#...##..#.
    ..#.##.......#.##.......#.##.......#.##.......#.##.......#.##.....  --->
    .#.#.#....#.#.#.#....#.#.#.#....#.#.#.#....#.#.#.#....#.#.#.#....#
    .#........#.#........#.#........#.#........#.#........#.#........#
    #.##...#...#.##...#...#.##...#...#.##...#...#.##...#...#.##...#...
    #...##....##...##....##...##....##...##....##...##....##...##....#
    .#..#...#.#.#..#...#.#.#..#...#.#.#..#...#.#.#..#...#.#.#..#...#.#  --->

    You start on the open square (.) in the top-left corner and need to reach the bottom (below the bottom-most row on your map).

    The toboggan can only follow a few specific slopes (you opted for a cheaper model that prefers rational numbers); start by counting all the trees you would encounter for the slope right 3, down 1:

    From your starting position at the top-left, check the position that is right 3 and down 1. Then, check the position that is right 3 and down 1 from there, and so on until you go past the bottom of the map.

    The locations you'd check in the above example are marked here with O where there was an open square and X where there was a tree:

    ..##.........##.........##.........##.........##.........##.......  --->
    #..O#...#..#...#...#..#...#...#..#...#...#..#...#...#..#...#...#..
    .#....X..#..#....#..#..#....#..#..#....#..#..#....#..#..#....#..#.
    ..#.#...#O#..#.#...#.#..#.#...#.#..#.#...#.#..#.#...#.#..#.#...#.#
    .#...##..#..X...##..#..#...##..#..#...##..#..#...##..#..#...##..#.
    ..#.##.......#.X#.......#.##.......#.##.......#.##.......#.##.....  --->
    .#.#.#....#.#.#.#.O..#.#.#.#....#.#.#.#....#.#.#.#....#.#.#.#....#
    .#........#.#........X.#........#.#........#.#........#.#........#
    #.##...#...#.##...#...#.X#...#...#.##...#...#.##...#...#.##...#...
    #...##....##...##....##...#X....##...##....##...##....##...##....#
    .#..#...#.#.#..#...#.#.#..#...X.#.#..#...#.#.#..#...#.#.#..#...#.#  --->

    In this example, traversing the map using this slope would cause you to encounter 7 trees.

    Starting at the top-left corner of your map and following a slope of right 3 and down 1, how many trees would you encounter?
    """


class Part2(Part[Data]):
    blurb = """
    Time to check the rest of the slopes - you need to minimize the probability of a sudden arboreal stop, after all.

    Determine the number of trees you would encounter if, for each of the following slopes, you start at the top-left corner and traverse the map all the way to the bottom:

        Right 1, down 1.
        Right 3, down 1. (This is the slope you already checked.)
        Right 5, down 1.
        Right 7, down 1.
        Right 1, down 2.

    In the above example, these slopes would find 2, 7, 3, 4, and 2 tree(s) respectively; multiplied together, these produce the answer 336.

    What do you get if you multiply together the number of trees encountered on each of the listed slopes?
    """

    def solve(self):
        answer = 1

        for dx, dy in zip([1, 3, 5, 7, 1], [1, 1, 1, 1, 2]):
            sol = super().solve(dx=dx, dy=dy)
            answer *= sol.answer

        return answer


register(Day3, Part1, Part2)