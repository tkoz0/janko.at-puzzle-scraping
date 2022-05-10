'''
Given a directory of puzzle data files (extracted from the htm files with the
extract_data.py script), this script will create a .jsonl file (1 JSON object
per line) with all the puzzles in that directory.

Usage: parse_data.py <puzzle> <out_file>
Puzzle is specified as its directory relative to /Raetsel on the website (/ for
the root, /Sudoku for Sudoku, and so on)
'''

import copy
import json
import os
import sys
from tqdm import tqdm
from typing import Dict, List, Union

from PuzzleParser import PuzzleParser, PropType
import PuzzleParserUtils as ppu

base_dir = os.path.normpath('../puzzle_x-janko/')

# puzzle path -> list of parsers to try (try in order until one works)
parsermap: Dict[str,List[PuzzleParser]] = dict()

'''
Puzzles with no x-janko files:
/Airando
/Aisurom
/Alphametics
/Alphametics/Additionen
/Alphametics/Goetter
/Alphametics/Klassisch
/Alphametics/Loy
/Alphametics/Metamatik
/Alphametics/Wurzeln
/Altay
/Amibo
/Analogien
/Autoren
/Banzu
/Battleships-Lighthouses
/Begriffe
/Biographien
/Blackbox
/Bleistifte
/Bodaburokku
/Bogdan
/Bolota
/Bonsan
/Branqueta
/Carroll
/Chatroom
/Chokuhashi
/Chronik
/Cross-The-Streams
/Diogenes
/Doppel-Schokolade
/Doughnut
/Ekici
/Friedman
'''

def createParsers():
    '''
    Setup the parsers used for each puzzle. Puzzles are annotated with which
    ones had to have the .x-janko files edited to complete successfully. Some

    '''
    psizegrid = ppu.makeParserSizeGrid()
    prcgrid = ppu.makeParserRCGrid()
    psizegridareas = ppu.makeParserSizeGrid(True)
    prcgridareas = ppu.makeParserRCGrid(True)
    #parsermap['/'] = None

    # /Abc-End-View
    p0 = copy.deepcopy(psizegrid)
    ppu.addParamsLabelsSize(p0,2)
    p0.addStr('diagonals')
    parsermap['/Abc-End-View'] = [p0]

    # /Abc-Kombi
    p0 = copy.deepcopy(prcgrid)
    ppu.addParamsLabelsRCDepth(p0)
    parsermap['/Abc-Kombi'] = [p0]

    # /Abc-Pfad
    p0 = PuzzleParser()
    ppu.addParamsCommon(p0)
    p0.addInt('size') # the grids happen to always be 7x7 and 5x5
    p0.addGrid('problem','size','size',lambda x:x+2,lambda x:x+2)
    p0.addGrid('solution','size','size')
    parsermap['/Abc-Pfad'] = [p0]

    # /Aisuban
    parsermap['/Aisuban'] = [psizegridareas,prcgridareas]

    # /Akari
    parsermap['/Akari'] = [psizegrid,prcgrid]

    # /Anglers (edited: 35)
    parsermap['/Anglers'] = [psizegrid,prcgrid]

    # /Aqre
    parsermap['/Aqre'] = [psizegridareas]

    # /Araf (moved: Different-Neighbors, Inequality)
    parsermap['/Araf'] = [psizegrid,prcgrid]

    # /Area-51
    p0 = copy.deepcopy(psizegrid)
    p0.addGrid('nodes','size','size',lambda x:x+1,lambda x:x+1)
    p1 = copy.deepcopy(prcgrid)
    p1.addGrid('nodes','rows','cols',lambda x:x+1,lambda x:x+1)
    parsermap['/Area-51'] = [p0,p1]

    # /Armyants
    parsermap['/Armyants'] = [psizegridareas,prcgridareas]

    # /Arukone
    parsermap['/Arukone'] = [psizegrid,prcgrid]

    # /Arukone-2
    parsermap['/Arukone-2'] = [psizegrid,prcgrid]

    # /Arukone-3
    parsermap['/Arukone-3'] = [psizegrid,prcgrid]

    # /Battlemines
    p0 = copy.deepcopy(psizegrid)
    p0.addStr('ships') # list of integers???
    parsermap['/Battlemines'] = [p0]

    # /Battleships (edited: 16,39)
    p0 = copy.deepcopy(psizegrid)
    ppu.addParamsLabelsSize(p0)
    p0.addStr('ships') # list of integers???
    parsermap['/Battleships'] = [p0]

    # /Battleships-Digital
    parsermap['/Battleships-Digital'] = parsermap['/Battleships']

    # /Battleships-Retrograde
    parsermap['/Battleships-Retrograde'] = parsermap['/Battleships']

    # /Bosanowa (edited: 34)
    parsermap['/Bosanowa'] = [psizegrid,prcgrid]

    # /Boxing-Match
    p0 = copy.deepcopy(psizegrid)
    p1 = copy.deepcopy(prcgrid)
    p0.addGrid('cellimage','size','size')
    p1.addGrid('cellimage','rows','cols')
    parsermap['/Boxing-Match'] = [p0,p1]

    # /Boxing-Match-2
    p0 = copy.deepcopy(psizegridareas)
    p1 = copy.deepcopy(prcgridareas)
    ppu.addParamsMinMax(p0)
    ppu.addParamsMinMax(p1)
    parsermap['/Boxing-Match-2'] = [p0,p1]

    # /Burokku
    p0 = copy.deepcopy(psizegrid)
    p0.addGrid('lines','size','size')
    parsermap['/Burokku'] = [p0]

    # /Campixu
    parsermap['/Campixu'] = [prcgridareas]

    # /Canal-View
    parsermap['/Canal-View'] = [psizegrid]

    # /Castle-Wall
    parsermap['/Castle-Wall'] = [psizegrid,prcgrid]

    # /Chocona
    parsermap['/Chocona'] = [psizegridareas,prcgridareas]

    # /Compass
    parsermap['/Compass'] = [psizegrid]

    # /Corral
    parsermap['/Corral'] = [psizegrid,prcgrid]

    # /Country-Road
    parsermap['/Country-Road'] = [psizegridareas,prcgridareas]

    # /Creek
    p0 = copy.deepcopy(psizegrid)
    p0.removeProp('problem')
    p0.addGrid('problem','size','size',lambda x:x+1,lambda x:x+1)
    p1 = copy.deepcopy(prcgrid)
    p1.removeProp('problem')
    p1.addGrid('problem','rows','cols',lambda x:x+1,lambda x:x+1)
    parsermap['/Creek'] = [p0,p1]

    # /Curving-Road
    parsermap['/Curving-Road'] = [psizegrid]

    # /Detektivschach
    p0 = copy.deepcopy(psizegrid)
    p0.addStr('pieces') # list of integers???
    p0.addInt('begin') # some have integer on begin line
    parsermap['/Detektivschach'] = [p0]

    # /Detour
    parsermap['/Detour'] = [psizegridareas,prcgridareas]

    # /Different-Neighbors
    parsermap['/Different-Neighbors'] = [psizegridareas]

    # /Dominion
    parsermap['/Dominion'] = [psizegrid]

    # /Dominos
    parsermap['/Dominos'] = [prcgrid]

    # /Doppelblock
    p0 = copy.deepcopy(prcgrid)
    ppu.addParamsLabelsRC(p0)
    parsermap['/Doppelblock'] = [p0]

    # /Dosun-Fuwari
    parsermap['/Dosun-Fuwari'] = [psizegridareas,prcgridareas]

    # /Double-Back
    parsermap['/Double-Back'] = [psizegridareas,prcgridareas]

    # /Dutch-Loop (edited: 2)
    parsermap['/Dutch-Loop'] = [psizegrid]

    # /Ebony-Ivory
    p0 = copy.deepcopy(psizegrid)
    ppu.addParamsLabelsSize(p0,2)
    p1 = copy.deepcopy(prcgrid)
    ppu.addParamsLabelsRC(p1,2)
    parsermap['/Ebony-Ivory'] = [p0,p1]

    # /Eins-bis-X
    p0 = copy.deepcopy(psizegridareas)
    ppu.addParamsLabelsSize(p0)
    parsermap['/Eins-bis-X'] = [p0]

    # /Elbow-Room (edited: 5)
    p0 = copy.deepcopy(psizegrid)
    ppu.addParamsLabelsSize(p0)
    p0.addStr('nlabels')
    p0.addGrid('celltext','size','size')
    parsermap['/Elbow-Room'] = [p0]

    # /Entry-Exit
    parsermap['/Entry-Exit'] = [psizegridareas]

    # /Eulero
    parsermap['/Eulero'] = [psizegrid]

    # /Factors
    parsermap['/Factors'] = [psizegridareas]

    # /Fillodoku
    p0 = copy.deepcopy(psizegrid)
    ppu.addParamsPattern(p0)
    parsermap['/Fillodoku'] = [p0]

    # /Fillomino
    parsermap['/Fillomino'] = [psizegrid,prcgrid]

    # /Firumatto
    parsermap['/Firumatto'] = [psizegrid]

    # /Fobidoshi
    parsermap['/Fobidoshi'] = [psizegrid]

    # /Foseruzu (edited: 47)
    parsermap['/Foseruzu'] = [psizegrid,prcgrid]

    # /Futoshiki
    p0 = copy.deepcopy(psizegrid)
    p0.removeProp('problem')
    p0.addGrid('problem','size','size',lambda x:2*x-1,lambda x:2*x-1)
    parsermap['/Futoshiki'] = [p0]

    # /Fuzuli
    parsermap['/Fuzuli'] = [psizegrid]

    # /Galaxien (edited: 445)
    parsermap['/Galaxien'] = [psizegrid,prcgrid]

    # TODO

    # /Sudoku
    p0 = copy.deepcopy(psizegrid) # size/rc covers almost all
    p1 = copy.deepcopy(prcgrid)
    p2 = PuzzleParser()
    ppu.addParamsPattern(p0)
    ppu.addParamsPattern(p1)
    p0.addNone('areas') # some have am empty areas property
    p1.addNone('areas')
    ppu.addParamsCommon(p2)
    p2.addGrid('problem',9,9) # some do not specify grid size (1161-1190)
    p2.addGrid('solution',9,9)
    parsermap['/Sudoku'] = [p0,p1,p2]

createParsers()

if __name__ == '__main__':

    puzzle = sys.argv[1]
    out_file = sys.argv[2]
    assert puzzle.startswith('/')
    dir_path = base_dir + ('' if puzzle == '/' else puzzle)
    file_name_list = sorted(os.listdir(dir_path))
    files = [dir_path+'/'+f for f in file_name_list if os.path.isfile(dir_path+'/'+f)]
    jsonl_data: List[Dict[str,Union[str,Dict[str,PropType]]]] = []

    tqdm.write('opening dir: '+dir_path+' (%d files)'%len(files))
    failed_files = []

    for file in tqdm(files):
        file_rel = puzzle+'/'+os.path.split(file)[1] # relative to /Raetsel dir
        tqdm.write('\nprocessing: '+file_rel)
        result = None
        errors = []
        for i,parser in enumerate(parsermap[puzzle]):
            result: Union[None,Dict[str,PropType]] = None
            try:
                result = parser.parse(open(file,'r'))
                break
            except Exception as e:
                errors.append('parser %d: '%i+str(e))
        if result is None:
            tqdm.write('\n'.join(errors))
            tqdm.write('ERROR: not parsed')
            failed_files.append(file)
        else:
            jsonl_data.append({'file':file_rel,'data':result})

    print()
    print('failed files (%d):'%len(failed_files))
    print('\n'.join(failed_files))
    print()
    print('writing '+out_file+' (%d objects)'%len(jsonl_data))
    outf = open(out_file,'w')
    for obj in jsonl_data:
        outf.write(json.dumps(obj,separators=(',',':'))+'\n')
    outf.close()
    print('done')

