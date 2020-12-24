from ..prelude import *

class Day3(Problem):

    def __init__(self, part):
        super().__init__(3, part)
        
        map = []
        for line in self.lines:
            row = [int(x == '#') for x in line]
            map.append(row)

        self.y = len(map)
        self.x = len(row)
        self.map = map
        
        self.info(f'x = {self.x}, y = {self.y}')

    @property
    def model(self):
        return r"""

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

    def solve(self, dx, dy):
        return solve_model(self.model, y1=self.y, x1=self.x, map=self.map, dx=dx,dy=dy)

    

class Part1(Day3):

    def __init__(self):
        super().__init__(1)

    def solve(self):
        sol = super().solve(3, 1)
        return sol.answer


class Part2(Day3):

    def __init__(self):
        super().__init__(2)

    def solve(self):
        answer = 1
                
        for dx,dy in zip([1, 3, 5, 7, 1], [1, 1, 1, 1, 2]):
            sol = super().solve(dx=dx,dy=dy)
            answer *= sol.answer

        return answer
