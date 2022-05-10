'''
Class for parsing puzzle files. The puzzles on janko.at appear to be formatted
as described here. They start with a line "begin\n" and end with line "end\n".
Between, they have properties that begin with a word such as "puzzle" or "size",
whose values may be on the same line, or on multiple following lines, depending
on the property.

Below is an example of the data (Sudoku #375):

<script id="data" type="application/x-janko">
begin
puzzle sudoku
author Otto Janko
solver Otto Janko
source https://www.janko.at/Raetsel/
info 9037-41-405125-0-254
unit 30
size 4
patternx 2
patterny 2
problem
- - 3 1
- - - -
- - - -
1 4 - -
solution
4 2 3 1
3 1 4 2
2 3 1 4
1 4 2 3
moves
Z2;ba,2;aa,4;ab,3;bb,1;ac,2;bc,3;cd,2;dd,3;dc,4;cc,1;
cb,4;db,2;
end
</script>

The "puzzle" property would be a string (on the same line). The "size" property
is an integer. The "problem" property is an integer grid. The "moves" property
is a multiple line string where each matches r";$" (use re.findall).
'''

import re
import sys
import tqdm
from typing import Any, Callable, Dict, Iterator, List, Pattern, Tuple, Union

from PeekableIterator import PeekableIterator

# property types
P_NONE = 0 # property only, no value
P_STR = 1 # same line string
P_INT = 2
P_GRID = 3 # needs rows+cols
P_STR_LONG = 4 # needs regex

PropType = Union[None,str,int,List[List[str]]]
GridParamType = Union[str,int]

class ParseException(Exception):
    ''' Thrown for parsing exceptions that should be fixed. '''

class PuzzleParser:
    '''
    Object representing the properties and types to expect when parsing a puzzle
    file.
    '''
    # Tuple[int,Any,Any] specifies property type and parameters it may use
    _props: Dict[str,Tuple[int,Any,Any,Any,Any]]
    _use_beg_end: bool
    _print: Callable[[str],Any] = sys.stderr.write # for printing errors
    def __init__(self, _use_beg_end: bool = True, err = tqdm.tqdm.write):
        ''' Initialize a new PuzzleParser '''
        self._props = dict()
        self._use_beg_end = _use_beg_end
        self._print = err
    def addNone(self, prop: str):
        assert prop != "" and prop not in self._props
        self._props[prop] = (P_NONE,None,None,None,None)
    def addStr(self, prop: str):
        assert prop != "" and prop not in self._props
        self._props[prop] = (P_STR,None,None,None,None)
    def addInt(self, prop: str):
        assert prop != "" and prop not in self._props
        self._props[prop] = (P_INT,None,None,None,None)
    def addGrid(self, prop: str, rows: GridParamType, cols: GridParamType,
            rowfunc: Callable[[int],int] = lambda x:x, colfunc: Callable[[int],int] = lambda x:x):
        assert prop != "" and prop not in self._props
        if isinstance(rows,str):
            assert rows in self._props
        if isinstance(cols,str):
            assert cols in self._props
        self._props[prop] = (P_GRID,rows,cols,rowfunc,colfunc)
    def addStrLong(self, prop: str, regex: Pattern):
        assert prop != "" and prop not in self._props
        self._props[prop] = (P_STR_LONG,regex,None,None,None)
    def removeProp(self, prop: str):
        del self._props[prop]
    def parse(self, input_lines: Iterator[str]) -> Dict[str,PropType]:
        lines = PeekableIterator(line.strip() for line in input_lines
                                    if line.strip() != '')
        result: Dict[str,PropType] = dict()
        if self._use_beg_end:
            try:
                assert lines.peek() == 'begin'
                next(lines)
            except:
                self._print('WARNING: no "begin" line\n')
        found_end = False
        while True:
            try:
                line = next(lines).split()
            except StopIteration:
                break
            if line == ['end']:
                found_end = True
                break
            if line[0] not in self._props:
                raise ParseException('unknown property: '+line[0])
            typenum,param1,param2,param3,param4 = self._props[line[0]]
            if line[0] in result:
                self._print('WARNING: duplicate property: '+line[0]+'\n')
                # pick a new name to avoid data loss
                while line[0] in result:
                    line[0] += '_'
            if typenum == P_NONE:
                result[line[0]] = None
                if len(line) > 1:
                    self._print('WARNING: extra data for none property: '+line[0]+'\n')
            elif typenum == P_STR:
                result[line[0]] = ' '.join(line[1:])
                if result[line[0]] == '':
                    self._print('WARNING: string property value empty: '+line[0]+'\n')
            elif typenum == P_INT:
                result[line[0]] = int(line[1])
                if len(line) > 2:
                    self._print('WARNING: extra data for int property: '+line[0]+'\n')
            elif typenum == P_GRID:
                # parse a grid, possibly convert to ints
                rows = 0
                cols = 0
                if isinstance(param1,str):
                    if param1 not in result:
                        raise ParseException('row length not specified before grid')
                    rows = result[param1]
                    assert isinstance(rows,int)
                else:
                    assert isinstance(param1,int)
                    rows = param1
                if isinstance(param2,str):
                    if param2 not in result:
                        raise ParseException('col length not specified before grid')
                    cols = result[param2]
                    assert isinstance(cols,int)
                else:
                    assert isinstance(param2,int)
                    cols = param2
                # apply functions to dimensions
                assert callable(param3)
                assert callable(param4)
                rows = param3(rows)
                cols = param4(cols)
                # parse grid
                grid: List[List[str]] = []
                for r in range(rows):
                    row = next(lines).split()
                    if len(row) != cols:
                        raise ParseException('row with invalid length (prop = %s, row = %d)'%(line[0],r))
                    grid.append(row)
                result[line[0]] = grid
            elif typenum == P_STR_LONG:
                longstr = ''
                assert isinstance(param1,Pattern)
                while True:
                    try:
                        if re.findall(param1,lines.peek()):
                            longstr += next(lines)
                        else:
                            break
                    except StopIteration:
                        break
                result[line[0]] = longstr
            else:
                assert 0
        if self._use_beg_end and not found_end:
            self._print('WARNING: no "end" line\n')
        try:
            next(lines)
            self._print('WARNING: extra data not read\n')
        except StopIteration:
            pass
        return result

