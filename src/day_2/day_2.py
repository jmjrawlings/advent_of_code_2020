from ..prelude import *

import string

log = setup_logger(__name__)

@dataclass
class Input:
    lower : int
    upper : int
    char  : str
    text  : str

    @property
    def n(self):
        return len(self.text)
   
# dir = cwd(2)


# char2num = {char: i for i,char in enumerate(string.ascii_lowercase)}
# num2char = {v:k for k,v in char2num.items()}


# def load_inputs(path = dir / 'input.txt') -> List[Input]:
        
#     inputs = []

#     with path.open() as src:
#         for line in src.readlines():
#             a,b,c = line.split()
#             lower, upper = a.split('-')
#             char = b[0]
#             text = c
#             input = Input(int(lower), int(upper), char, text)
#             inputs.append(input)

#     log.info(f'{path} -> {len(inputs)} inputs')
#     return inputs


# def part_1():

#     model = r"""
#     include "globals.mzn";

#     int: cols;
#     int: rows;
    
#     set of int: CHAR = -1 .. 26;
#     set of int: ROW = 1 .. rows;
#     set of int: COL = 1.. cols;
        
#     array[ROW, COL] of CHAR: passwords;
#     array[ROW] of COL: lowers;
#     array[ROW] of COL: uppers;
#     array[ROW] of CHAR: chars;
        
#     array[ROW] of var bool: valid;

#     var int: answer;
            
#     constraint forall (i in ROW) (
#         let 
#             {
#             var 0..cols: n = count(row(passwords,i), chars[i]);
#             var int: lower = lowers[i];
#             var int: upper = uppers[i];
#             }
#         in
#             valid[i] = (lower <= n /\ n <= upper)
#     );
        
#     constraint answer = sum(valid);
#     """
#     inputs = load_inputs()[:]

#     rows = len(inputs)
#     cols = max(i.n for i in inputs)

#     passwords = []
#     lowers = []
#     uppers = []
#     chars = []
    
#     for i in inputs:
#         row = [char2num[c] for c in i.text] + [-1]*(cols - i.n)
#         passwords.append(row)
#         lowers.append(i.lower)
#         uppers.append(i.upper)
#         chars.append(char2num[i.char])
        
#     result = solve_model(
#         model,
#         lowers=lowers,
#         uppers=uppers,
#         passwords=passwords,
#         chars=chars,
#         rows=rows,
#         cols=cols)

#     log.info(f'part 1 = {result.answer}')        

#     return inputs



# def part_2():

#     model = r"""
#     include "globals.mzn";

#     int: cols;
#     int: rows;
    
#     set of int: CHAR = -1 .. 26;
#     set of int: ROW = 1 .. rows;
#     set of int: COL = 1.. cols;
        
#     array[ROW, COL] of CHAR: passwords;
#     array[ROW] of COL: first_index;
#     array[ROW] of COL: second_index;
#     array[ROW] of CHAR: chars;
    
#     array[ROW] of var bool: valid;

#     var int: answer;
            
#     constraint forall (i in ROW) (
#         let
#             {
#             CHAR: char = chars[i];
#             COL: j = first_index[i];
#             COL: k = second_index[i];
#             CHAR: u = passwords[i,j];
#             CHAR: v = passwords[i,k]
#             }
#         in
#             valid[i] = (u = char) xor (v = char)
#     );
        
#     constraint answer = sum(valid);
#     """
#     inputs = load_inputs()[:]

#     rows = len(inputs)
#     cols = max(i.n for i in inputs)
#     log.info(f'max input = {cols}')

#     passwords = []
#     firsts = []
#     seconds = []
#     chars = []
    
#     for i in inputs:
#         row = [char2num[c] for c in i.text] + [-1]*(cols - i.n)
#         passwords.append(row)
#         firsts.append(i.lower)
#         seconds.append(i.upper)
#         chars.append(char2num[i.char])
        
#     result = solve_model(
#         model,
#         first_index=firsts,
#         second_index=seconds,
#         passwords=passwords,
#         chars=chars,
#         rows=rows,
#         cols=cols)

#     log.info(f'part 2 = {result.answer}')

#     return inputs