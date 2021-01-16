from ..prelude import *

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


class Day2(Day[Data]):
    num = 2
    title = "Password Philosophy"

    def data(self, lines):
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


class Part1(Part[Data]):

    blurb = r"""
    Your flight departs in a few days from the coastal airport; the easiest way down to the coast from here is via toboggan.

    The shopkeeper at the North Pole Toboggan Rental Shop is having a bad day. "Something's wrong with our computers; we can't log in!" You ask if you can take a look.

    Their password database seems to be a little corrupted: some of the passwords wouldn't have been allowed by the Official Toboggan Corporate Policy that was in effect when they were chosen.

    To try to debug the problem, they have created a list (your puzzle input) of passwords (according to the corrupted database) and the corporate policy when that password was set.

    For example, suppose you have the following list:

    1-3 a: abcde
    1-3 b: cdefg
    2-9 c: ccccccccc

    Each line gives the password policy and then the password. The password policy indicates the lowest and highest number of times a given letter must appear for the password to be valid. For example, 1-3 a means that the password must contain a at least 1 time and at most 3 times.

    In the above example, 2 passwords are valid. The middle password, cdefg, is not; it contains no instances of b, but needs at least 1. The first and third passwords are valid: they contain one a or nine c, both within the limits of their respective policies.

    How many passwords are valid according to their policies?
    """

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

    def formulate(self, data: Data):

        rows = data.n
        cols = max(len(x) for x in data.password)

        passwords = []
        chars = []

        for char, pword in zip(data.char, data.password):
            password = [char2num[c] for c in pword] + [-1] * (cols - len(pword))
            passwords.append(password)
            chars.append(char2num[char])

        return dict(
            model=self.model,
            lowers=data.lower,
            uppers=data.upper,
            passwords=passwords,
            chars=chars,
            rows=rows,
            cols=cols,
        )


class Part2(Part[Data]):

    blurb = r"""
    While it appears you validated the passwords correctly, they don't seem to be what the Official Toboggan Corporate Authentication System is expecting.

    The shopkeeper suddenly realizes that he just accidentally explained the password policy rules from his old job at the sled rental place down the street! The Official Toboggan Corporate Policy actually works a little differently.

    Each policy actually describes two positions in the password, where 1 means the first character, 2 means the second character, and so on. (Be careful; Toboggan Corporate Policies have no concept of "index zero"!) Exactly one of these positions must contain the given letter. Other occurrences of the letter are irrelevant for the purposes of policy enforcement.

    Given the same example list from above:

        1-3 a: abcde is valid: position 1 contains a and position 3 does not.
        1-3 b: cdefg is invalid: neither position 1 nor position 3 contains b.
        2-9 c: ccccccccc is invalid: both position 2 and position 9 contain c.

    How many passwords are valid according to the new interpretation of the policies?
    """

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

    def formulate(self, data: Data):

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
            model=self.model,
            first_index=data.lower,
            second_index=data.upper,
            passwords=passwords,
            chars=chars,
            rows=rows,
            cols=cols,
        )


register(Day2, Part1, Part2)