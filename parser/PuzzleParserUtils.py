'''
Common functions for managing PuzzleParser objects.
'''

import re
from typing import Type, Union

from PuzzleParser import PuzzleParser

TypeIntOrStr = Union[Type[int],Type[str]]

def addParamsCommon(p: PuzzleParser):
    p.addStr('puzzle')
    p.addStr('author')
    p.addStr('solver')
    p.addStrLong('moves',re.compile(r';$'))
    p.addStr('source')
    p.addStr('rights')
    p.addStr('check')
    p.addInt('unit')
    p.addInt('unitsize')
    p.addInt('depth')
    p.addStr('info')
    p.addStr('infotext')
    p.addStr('date')
    p.addStr('title')
    p.addStr('variant')
    p.addStr('layout')
    p.addStr('options')
    p.addStr('mail')
    p.addStr('pid')

def addParamsRCGrid(p: PuzzleParser, areas: bool = False):
    p.addInt('rows')
    p.addInt('cols')
    p.addGrid('problem','rows','cols')
    p.addGrid('solution','rows','cols')
    if areas:
        p.addGrid('areas','rows','cols')

def addParamsSizeGrid(p: PuzzleParser, areas: bool = False):
    p.addInt('size')
    p.addGrid('problem','size','size')
    p.addGrid('solution','size','size')
    if areas:
        p.addGrid('areas','size','size')

def addParamsLabelsRC(p: PuzzleParser, count: int = 1):
    p.addGrid('rlabels',count,'rows')
    p.addGrid('clabels',count,'cols')

def addParamsLabelsSize(p: PuzzleParser, count: int = 1):
    p.addGrid('rlabels',count,'size')
    p.addGrid('clabels',count,'size')

def addParamsLabelsRCDepth(p: PuzzleParser):
    p.addGrid('rlabels','depth','rows')
    p.addGrid('clabels','depth','cols')

def addParamsPattern(p: PuzzleParser):
    p.addInt('pattern')
    p.addInt('patternx')
    p.addInt('patterny')

def addParamsMinMax(p: PuzzleParser):
    p.addInt('min')
    p.addInt('max')

def makeParserRCGrid(areas: bool = False):
    p = PuzzleParser(True)
    addParamsCommon(p)
    addParamsRCGrid(p,areas)
    return p

def makeParserSizeGrid(areas: bool = False):
    p = PuzzleParser(True)
    addParamsCommon(p)
    addParamsSizeGrid(p,areas)
    return p

