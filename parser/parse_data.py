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
/Gedichte
/Gedichte/07
/Gedichte/10
/H2O
/Hiroimono
/Hitori-Ribashi
/Ichimaga
/International-Borders
/Kalkulu
/Kanjo
/Karakiri
/Kazunori
/Kreuzzahlen
/Kuroclone
/Lagioia
/Laterale
/Literatur
/LMI
/Logicals
/Logik
/Mainarizumu
/Manekingeto
/Mathematik
/Mejirinku
/Milchkaffee
/Milchtee
/Mittelweg
/Molekularis
'''

def createParsers():
    '''
    Setup the parsers used for each puzzle. Puzzles are annotated with which
    ones had to have the .x-janko files edited to complete successfully. Some
    have special files which are moved out to be dealt with separately.

    '''
    # common parsers
    psizegrid = ppu.makeParserSizeGrid()
    prcgrid = ppu.makeParserRCGrid()
    psizegridareas = ppu.makeParserSizeGrid(True)
    prcgridareas = ppu.makeParserRCGrid(True)
    psizegrid_labels1 = copy.deepcopy(psizegrid)
    psizegrid_labels2 = copy.deepcopy(psizegrid)
    prcgrid_labels1 = copy.deepcopy(prcgrid)
    prcgrid_labels2 = copy.deepcopy(prcgrid)
    psizegridareas_labels1 = copy.deepcopy(psizegridareas)
    psizegridareas_labels2 = copy.deepcopy(psizegridareas)
    prcgridareas_labels1 = copy.deepcopy(prcgridareas)
    prcgridareas_labels2 = copy.deepcopy(prcgridareas)
    #parsermap['/'] = None
    ppu.addParamsLabelsSize(psizegrid_labels1)
    ppu.addParamsLabelsSize(psizegrid_labels2,2)
    ppu.addParamsLabelsRC(prcgrid_labels1)
    ppu.addParamsLabelsRC(prcgrid_labels2,2)
    ppu.addParamsLabelsSize(psizegridareas_labels1)
    ppu.addParamsLabelsSize(psizegridareas_labels2,2)
    ppu.addParamsLabelsRC(prcgridareas_labels1)
    ppu.addParamsLabelsRC(prcgridareas_labels2,2)

    # Setup parsers for all puzzles

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
    parsermap['/Doppelblock'] = [prcgrid_labels1]

    # /Dosun-Fuwari
    parsermap['/Dosun-Fuwari'] = [psizegridareas,prcgridareas]

    # /Double-Back
    parsermap['/Double-Back'] = [psizegridareas,prcgridareas]

    # /Dutch-Loop (edited: 2)
    parsermap['/Dutch-Loop'] = [psizegrid]

    # /Ebony-Ivory
    parsermap['/Ebony-Ivory'] = [psizegrid_labels2,prcgrid_labels2]

    # /Eins-bis-X
    parsermap['/Eins-bis-X'] = [psizegridareas_labels1]

    # /Elbow-Room (edited: 5)
    p0 = copy.deepcopy(psizegrid_labels1)
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

    # /Gappy
    parsermap['/Gappy'] = [prcgrid_labels1,psizegrid_labels1]

    # /Geradeweg
    parsermap['/Geradeweg'] = [psizegrid]

    # /Gokigen-Naname (edited: 184)
    p0 = copy.deepcopy(psizegrid)
    p1 = copy.deepcopy(prcgrid)
    p0.removeProp('problem')
    p0.addGrid('problem','size','size',lambda x:x+1,lambda x:x+1)
    p1.removeProp('problem')
    p1.addGrid('problem','rows','cols',lambda x:x+1,lambda x:x+1)
    parsermap['/Gokigen-Naname'] = [p0,p1]

    # /Grades
    parsermap['/Grades'] = [psizegrid_labels2]

    # /Grand-Tour
    parsermap['/Grand-Tour'] = [psizegrid]

    # /Gyokuseki
    parsermap['/Gyokuseki'] = [psizegrid_labels2]

    # /Hakoiri (edited: 75)
    parsermap['/Hakoiri'] = [psizegridareas]

    # /Hakyuu
    parsermap['/Hakyuu'] = [psizegridareas,prcgridareas]

    # /Hamusando
    parsermap['/Hamusando'] = [psizegrid_labels1]

    # /Hanare
    parsermap['/Hanare'] = [psizegridareas]

    # /Hashi (edited: 572)
    parsermap['/Hashi'] = [psizegrid,prcgrid]

    # /Hashi-2
    parsermap['/Hashi-2'] = [psizegrid,prcgrid]

    # /Hebi-Ichigo (edited: 64) (moved: Basilisks, Seconds)
    parsermap['/Hebi-Ichigo'] = [psizegrid,prcgrid]

    # /Herugolf
    parsermap['/Herugolf'] = [psizegrid,prcgrid]

    # /Heyawake (edited: 576)
    parsermap['/Heyawake'] = [prcgridareas,psizegridareas]

    # /Hidoku
    parsermap['/Hidoku'] = [psizegrid]

    # /Hitori
    parsermap['/Hitori'] = [prcgrid,psizegrid]

    # /Hotaru-Beam
    p0 = copy.deepcopy(psizegrid)
    p0.removeProp('problem')
    p0.addGrid('problem','size','size',lambda x:x+1,lambda x:x+1)
    p0.addGrid('rlabels',2,'size',lambda x:x,lambda x:x-1)
    p0.addGrid('clabels',2,'size',lambda x:x,lambda x:x-1)
    parsermap['/Hotaru-Beam'] = [p0]

    # /Irasuto
    parsermap['/Irasuto'] = [psizegrid]

    # /Japanische-Summen
    parsermap['/Japanische-Summen'] = [psizegrid]

    # /Juosan
    parsermap['/Juosan'] = [psizegridareas,prcgridareas]

    # /Kaero
    parsermap['/Kaero'] = [psizegridareas,prcgridareas]

    # /Kakurasu
    p2 = copy.deepcopy(prcgrid_labels1)
    p2.addInt('begin') # some have integer on begin line
    parsermap['/Kakurasu'] = [psizegrid_labels1,prcgrid_labels1,p2]

    # /Kakuro
    parsermap['/Kakuro'] = [prcgrid,psizegrid]

    # /Kapetto
    parsermap['/Kapetto'] = [psizegrid]

    # /Kendoku
    parsermap['/Kendoku'] = [psizegridareas]

    # /Ketten
    parsermap['/Ketten'] = [psizegrid,prcgrid]

    # /Kinkonkan
    parsermap['/Kinkonkan'] = [psizegridareas_labels2]

    # /Knickweg
    parsermap['/Knickweg'] = [psizegrid_labels1]

    # /Knossos
    parsermap['/Knossos'] = [psizegrid]

    # /Koburin
    parsermap['/Koburin'] = [psizegrid]

    # /Kojun
    parsermap['/Kojun'] = [psizegridareas]

    # /Kuromasu
    parsermap['/Kuromasu'] = [prcgrid,psizegrid]

    # /Kuroshiro
    parsermap['/Kuroshiro'] = [psizegrid]

    # /Kuroshuto
    parsermap['/Kuroshuto'] = [psizegrid]

    # /Kurotto (edited: 82)
    parsermap['/Kurotto'] = [psizegrid,prcgrid]

    # /Lampions
    p0 = copy.deepcopy(psizegrid)
    p0.addInt('begin') # some have integer on begin line
    parsermap['/Lampions'] = [p0]

    # /Lateinische-Summen
    parsermap['/Lateinische-Summen'] = [psizegrid,prcgrid]

    # /Leuchttuerme
    parsermap['/Leuchttuerme'] = [prcgrid,psizegrid]

    # /Licht-Schatten
    parsermap['/Licht-Schatten'] = [psizegrid]

    # /Linesweeper
    parsermap['/Linesweeper'] = [psizegrid,prcgrid]

    # /LITS (edited: 281,282,284,285,286,287,288,289,290)
    parsermap['/LITS'] = [prcgridareas,psizegridareas]

    # /Maeander (edited: 24)
    parsermap['/Maeander'] = [psizegrid,prcgrid]

    # /Maeanderzahlen (edited: 24)
    parsermap['/Maeanderzahlen'] = [psizegridareas]

    # /Magnete
    parsermap['/Magnete'] = [psizegridareas_labels2]

    # /Makaro
    parsermap['/Makaro'] = [psizegridareas]

    # /Mastermind
    p0 = copy.deepcopy(psizegrid)
    p1 = copy.deepcopy(prcgrid)
    p0.removeProp('problem')
    p0.addGrid('problem','size','size',lambda x:x,lambda x:x+2)
    p0.removeProp('solution')
    p0.addGrid('solution',1,'size')
    p0.addStr('unique')
    p1.removeProp('problem')
    p1.addGrid('problem','rows','cols',lambda x:x,lambda x:x+2)
    p1.removeProp('solution')
    p1.addGrid('solution',1,'cols')
    p1.addStr('unique')
    p2 = copy.deepcopy(p1) # some have full length solution row
    p2.removeProp('solution')
    p2.addGrid('solution',1,'cols',lambda x:x,lambda x:x+2)
    parsermap['/Mastermind'] = [p0,p1,p2]

    # /Masyu
    parsermap['/Masyu'] = [psizegrid,prcgrid]

    # /Masyu-2
    parsermap['/Masyu-2'] = [prcgrid]

    # /Mathrax
    p0 = copy.deepcopy(psizegrid)
    p0.addGrid('nodes','size','size',lambda x:x-1,lambda x:x-1)
    parsermap['/Mathrax'] = [p0]

    # /Mauerbau
    parsermap['/Mauerbau'] = [psizegrid,prcgrid]

    # /Meadows
    parsermap['/Meadows'] = [psizegrid]

    # /Minesweeper
    p0 = copy.deepcopy(prcgrid)
    p1 = copy.deepcopy(psizegrid)
    p0.addInt('mines')
    p1.addInt('mines')
    parsermap['/Minesweeper'] = [p0,p1]

    # /Mintonette
    parsermap['/Mintonette'] = [psizegrid]

    # /Miss-Lupun (edited: 171)
    p0 = copy.deepcopy(prcgrid)
    p0.removeProp('problem')
    p0.addGrid('problem','rows','cols',lambda x:2*x-1,lambda x:2*x-1,'s')
    parsermap['/Miss-Lupun'] = [p0]

    # /Mochikoro
    parsermap['/Mochikoro'] = [psizegrid]

    # /Mochinyoro
    parsermap['/Mochinyoro'] = [psizegrid,prcgrid]

    # /Moonsun (edited: 19)
    parsermap['/Moonsun'] = [psizegridareas,prcgridareas]

    # /Mosaik
    parsermap['/Mosaik'] = [prcgrid,psizegrid]

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
                if isinstance(e,AssertionError):
                    raise e
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

