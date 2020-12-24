from _pytest.mark import param
from ..prelude import *
 
@dataclass(frozen = True, eq = True)
class Bag:
    style : str
    color : str

    def __repr__(self):
        return f'{self.style}.{self.color}'


@dataclass
class Rule:
    outer : Bag
    inner : Bag
    count : int

    def __repr__(self):
        return f'<{self.outer} // {self.count} {self.inner}>'

@dataclass
class Data:
    bags  : Set[Bag]
    rules : List[Rule]

    @property
    def n_rule(self):
        return len(self.rules)
    
    @property
    def n_bag(self):
        return len(self.bags)

    def __repr__(self):
        return f'<{self.n_bag} bags // {self.n_rule} rules>'

    

class Part1(Problem[Data]):
    
    day  = 7
    part = 1 

    def parse_line(self, line : str):
        # posh chartreuse bags contain 4 faded violet bags, 3 pale black bags, 2 posh coral bags.
        tokens = line.split(' ')
        outer_type, outer_color, _, _ = tokens[:4]

        # no inner bags
        if tokens[4] == 'no':
            return
            yield

        # many inner bags
        outer = Bag(outer_type, outer_color)       
        for x in ' '.join(tokens[4:]).split(', '):
            count, inner_type, inner_color, _ = x.split(' ')
            inner = Bag(inner_type, inner_color)
            rule = Rule(outer, inner, int(count))
            yield rule
            

    def setup(self):
        rules = []
        for line in self.lines:
            for rule in self.parse_line(line):
                rules.append(rule)

        bags = set(bag for rule in rules for bag in [rule.inner, rule.outer])
        data = Data(bags, rules)
        return data

    def solve(self, data : Data) -> int:

        bag2idx, idx2bag = index_map(data.bags)
                
        model = r"""
        int : n_bag;
        int : n_rule;
        int : max_n;
        
        set of int : BAG = 0 .. n_bag - 1;
        set of int : RULE = 1 .. n_rule;
                
        array[RULE] of BAG: outer;
        array[RULE] of BAG: inner;
        array[RULE] of int: count;
                
        array[BAG, BAG] of var 0 .. max_n: contains;
                
        %constraint forall (i in RULE) (
        %    contains[outer[i], inner[i]] = count[i]
        %);
        
        """
        return 0
        rules = data.rules[:10]
        n_rule = len(rules)
        logging.error(n_rule)

        sol = solve_model(
            model,
            solver = 'chuffed',
            n_bag=data.n_bag,
            n_rule=n_rule,
            max_n=max(rule.count for rule in rules),
            outer=[bag2idx[rule.outer] for rule in rules],
            inner=[bag2idx[rule.inner] for rule in rules],
            count=[rule.count for rule in rules]
            )
        return sol.answer


class Part2(Part1):
    pass