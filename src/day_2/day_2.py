from src import *

log = setup_logger(__name__)


@attr.s(repr=False)
class Data:
    lower: List[int] = attr.ib(factory=list)
    upper: List[int] = attr.ib(factory=list)
    char: List[str] = attr.ib(factory=list)
    password: List[str] = attr.ib(factory=list)

    @property
    def n(self):
        return len(self.password)

    def __repr__(self) -> str:
        return f"<{len(self.lower)} items>"


char2num = {char: i for i, char in enumerate(string.ascii_lowercase)}
num2char = {v: k for k, v in char2num.items()}


class Day2(Problem[Data]):
    day = 2

    @classmethod
    def parse(cls, lines):
        data = Data()
        for line in lines:
            a, b, password = line.split()
            lower, upper = a.split("-")
            char = b[0]
            data.lower.append(int(lower))
            data.upper.append(int(upper))
            data.char.append(char)
            data.password.append(password)

        return data


class Part1(Day2):
    part = 1

    model = r"""
    include "globals.mzn";

    int: cols;
    int: rows;

    set of int: CHAR = -1 .. 26;
    set of int: ROW = 1 .. rows;
    set of int: COL = 1.. cols;

    array[ROW, COL] of CHAR: passwords;
    array[ROW] of COL: lowers;
    array[ROW] of COL: uppers;
    array[ROW] of CHAR: chars;

    array[ROW] of var bool: valid;

    constraint forall (i in ROW) (
        let
            {
            var 0..cols: n = count(row(passwords,i), chars[i]);
            var int: lower = lowers[i];
            var int: upper = uppers[i];
            }
        in
            valid[i] = (lower <= n /\ n <= upper)
    );

    solve maximize sum(valid);
    """

    @classmethod
    def formulate(cls, data: Data):

        rows = data.n
        cols = max(len(x) for x in data.password)

        passwords = []
        chars = []

        for char, pword in zip(data.char, data.password):
            password = [char2num[c] for c in pword] + [-1] * (cols - len(pword))
            passwords.append(password)
            chars.append(char2num[char])

        return dict(
            model=cls.model,
            lowers=data.lower,
            uppers=data.upper,
            passwords=passwords,
            chars=chars,
            rows=rows,
            cols=cols,
        )


class Part2(Day2):

    model = r"""
        include "globals.mzn";

        int: cols;
        int: rows;

        set of int: CHAR = -1 .. 26;
        set of int: ROW = 1 .. rows;
        set of int: COL = 1.. cols;

        array[ROW, COL] of CHAR: passwords;
        array[ROW] of COL: first_index;
        array[ROW] of COL: second_index;
        array[ROW] of CHAR: chars;

        array[ROW] of var bool: valid;

        constraint forall (i in ROW) (
            let
                {
                CHAR: char = chars[i];
                COL: j = first_index[i];
                COL: k = second_index[i];
                CHAR: u = passwords[i,j];
                CHAR: v = passwords[i,k]
                }
            in
                valid[i] = (u = char) xor (v = char)
        );

        solve maximize sum(valid);
        """

    @classmethod
    def formulate(cls, data: Data):

        rows = len(data.lower)
        cols = max(len(p) for p in data.password)

        passwords = []
        chars = []

        for p in data.password:
            row = [char2num[c] for c in p] + [-1] * (cols - len(p))
            passwords.append(row)

        for c in data.char:
            chars.append(char2num[c])

        return dict(
            model=cls.model,
            first_index=data.lower,
            second_index=data.upper,
            passwords=passwords,
            chars=chars,
            rows=rows,
            cols=cols,
        )