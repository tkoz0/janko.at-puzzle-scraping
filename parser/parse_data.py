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
import re
import sys
from tqdm import tqdm
from typing import Dict, List, Union

from PuzzleParser import PuzzleParser, PropType
import PuzzleParserUtils as ppu

base_dir = os.path.normpath('../puzzle_x-janko/')

# puzzle path -> list of parsers to try (try in order until one works)
parsermap: Dict[str,List[PuzzleParser]] = dict()

# empty directories (no parser needed)
noparserlist = [
'', # for root dir
'/Aisurom',
'/Alphametics',
'/Alphametics/Additionen',
'/Alphametics/Goetter',
'/Alphametics/Klassisch',
'/Alphametics/Loy',
'/Alphametics/Metamatik',
'/Alphametics/Wurzeln',
'/Altay',
'/Amibo',
'/Analogien',
'/Autoren',
'/Banzu',
'/Battleships-Lighthouses',
'/Begriffe',
'/Biographien',
'/Blackbox',
'/Bleistifte',
'/Bodaburokku',
'/Bogdan',
'/Bolota',
'/Bonsan',
'/Branqueta',
'/Carroll',
'/Chatroom',
'/Chokuhashi',
'/Chronik',
'/Cross-The-Streams',
'/Diogenes',
'/Doppel-Schokolade',
'/Doughnut',
'/Ekici',
'/Friedman',
'/Friedman/img',
'/Gedichte',
'/Gedichte/04',
'/Gedichte/07',
'/Gedichte/08',
'/Gedichte/10',
'/H2O',
'/Hiroimono',
'/Hitori-Ribashi',
'/Ichimaga',
'/International-Borders',
'/Kalkulu',
'/Kanjo',
'/Karakiri',
'/Kazunori',
'/Kreuzzahlen',
'/Kuroclone',
'/Lagioia',
'/Laterale',
'/Literatur',
'/LMI',
'/Logicals',
'/Logik',
'/Mainarizumu',
'/Manekingeto',
'/Mathematik',
'/Mejirinku',
'/Milchkaffee',
'/Mittelweg',
'/Molekularis',
'/Nagareru',
'/Nagewawa',
'/Nanro/Hex',
'/Nikoli',
'/Nikoli/img',
'/Nishiyama',
'/Null-Zwei-Fuenf',
'/OAPC',
'/Out-Of-Sight',
'/Pathfinder',
'/Peeters',
'/Pentominos',
'/Physik',
'/Polyominos',
'/Portugalov',
'/Rectslider',
'/Renban-Madoguchi',
'/Saltatori',
'/Sashikaku',
'/Sphinx',
'/Stained-Glass',
'/Statue-Park',
'/Sudoku/Subset',
'/Summandum',
'/Takahiko',
'/Targets',
'/Tawa',
'/Triplace',
'/Trivia',
'/Um-Die-Ecke-Gedacht',
'/Vermischtes',
'/Wortwandlung',
'/WPF',
'/Zahlenpfad',
'/Zeiger',
'/img',
'/img2'
]

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

    # /Airando
    parsermap['/Airando'] = [psizegrid]

    # /Aisuban
    parsermap['/Aisuban'] = [psizegridareas,prcgridareas]

    # /Akari
    parsermap['/Akari'] = [psizegrid,prcgrid]

    # /Anglers (edited: 35)
    parsermap['/Anglers'] = [psizegrid,prcgrid]

    # /Aqre (edited: 58)
    parsermap['/Aqre'] = [psizegridareas]

    # /Araf (moved: Different-Neighbors, Inequality)
    parsermap['/Araf'] = [psizegrid,prcgrid]

    # /Area-51 (edited: 12)
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

    # /Battlemines (edited: 234)
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

    # /Bosanowa
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

    # /Gokigen-Naname (edited: 184,747,748,757,758)
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

    # /Hakoiri
    parsermap['/Hakoiri'] = [psizegridareas]

    # /Hakyuu
    parsermap['/Hakyuu'] = [psizegridareas,prcgridareas]

    # /Hamusando
    parsermap['/Hamusando'] = [psizegrid_labels1]

    # /Hanare
    parsermap['/Hanare'] = [psizegridareas]

    # /Hashi
    parsermap['/Hashi'] = [psizegrid,prcgrid]

    # /Hashi-2
    parsermap['/Hashi-2'] = [psizegrid,prcgrid]

    # /Hebi-Ichigo (edited: 64) (moved: Basilisks, Seconds)
    parsermap['/Hebi-Ichigo'] = [psizegrid,prcgrid]

    # /Herugolf
    parsermap['/Herugolf'] = [psizegrid,prcgrid]

    # /Heyawake
    parsermap['/Heyawake'] = [prcgridareas,psizegridareas]

    # /Heyawake/AYE (edited: 59,177)
    parsermap['/Heyawake/AYE'] = [prcgridareas,psizegridareas]

    # /Heyawake/AYE-2 (edited: 21,31,34,44,45)
    parsermap['/Heyawake/AYE-2'] = [prcgridareas,psizegridareas]

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

    # /Milchtee
    parsermap['/Milchtee'] = [psizegrid]

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

    # /Moonsun
    parsermap['/Moonsun'] = [psizegridareas,prcgridareas]

    # /Mosaik
    parsermap['/Mosaik'] = [prcgrid,psizegrid]

    # /Nachbarn
    parsermap['/Nachbarn'] = [psizegrid,prcgrid]

    # /Nanbaboru
    parsermap['/Nanbaboru'] = [psizegrid]

    # /Nanro
    parsermap['/Nanro'] = [psizegridareas]

    # /Nanro/Double
    parsermap['/Nanro/Double'] = [psizegridareas]

    # /Nanro/Doubleback
    parsermap['/Nanro/Doubleback'] = [psizegridareas]

    # /Nanro/Litro
    p0 = copy.deepcopy(psizegridareas)
    p0.addGrid('cornertext','size','size')
    parsermap['/Nanro/Litro'] = [p0]

    # /Nanro/Loop
    parsermap['/Nanro/Loop'] = [psizegridareas]

    # /Nanro/Odd-Even
    parsermap['/Nanro/Odd-Even'] = [psizegridareas]

    # /Nanro/Outside
    p0 = copy.deepcopy(psizegridareas_labels2)
    p0.addStr('nlabels')
    parsermap['/Nanro/Outside'] = [p0]

    # /Nanro/Signpost (deleted: 15,16,17,18)
    parsermap['/Nanro/Signpost'] = parsermap['/Nanro/Litro']

    # /Naoki (moved: all)

    # /Nawabari
    parsermap['/Nawabari'] = [psizegrid]

    # /Nondango
    parsermap['/Nondango'] = [psizegridareas,prcgridareas]

    # /Nonogramme
    p2 = copy.deepcopy(prcgrid)
    p2.addGrid('rlabels','rows','cols',flags='s')
    p2.addGrid('clabels','cols','rows',flags='s')
    p3 = copy.deepcopy(psizegrid)
    p3.addGrid('rlabels','size','size',flags='s')
    p3.addGrid('clabels','size','size',flags='s')
    parsermap['/Nonogramme'] = [prcgrid,psizegrid,p2,p3]

    # /Nonograms
    parsermap['/Nonograms'] = parsermap['/Nonogramme']

    # /Norinori
    parsermap['/Norinori'] = [psizegridareas,prcgridareas]

    # /Nuribou
    parsermap['/Nuribou'] = [psizegrid]

    # /Nurikabe
    parsermap['/Nurikabe'] = [prcgrid,psizegrid]

    # /Nurikabe-Pairs
    parsermap['/Nurikabe-Pairs'] = [psizegrid]

    # /Nurimaze
    parsermap['/Nurimaze'] = [psizegridareas,prcgridareas]

    # /Nurimaze/Dead-End
    p1 = copy.deepcopy(psizegridareas)
    p1.addInt('begin') # handle case with integer on begin line
    parsermap['/Nurimaze/Dead-End'] = [psizegridareas,p1]

    # /Nurimaze/Domino
    parsermap['/Nurimaze/Domino'] = [psizegridareas]

    # /Nurimaze/Forbidden-Four
    parsermap['/Nurimaze/Forbidden-Four'] = [psizegridareas]

    # /Nurimisaki
    parsermap['/Nurimisaki'] = [psizegrid]

    # /Oasis
    parsermap['/Oasis'] = [psizegrid]

    # /Partiti
    p0 = copy.deepcopy(psizegrid)
    ppu.addParamsMinMax(p0)
    p0.addGrid('cornertext','size','size')
    parsermap['/Partiti'] = [p0]

    # /Patchwork
    parsermap['/Patchwork'] = [psizegridareas]

    # /Peintoeria
    parsermap['/Peintoeria'] = [psizegridareas]

    # /Pfeilnetz
    parsermap['/Pfeilnetz'] = [psizegrid]

    # /Pfeilpfad (edited: 175)
    p0 = copy.deepcopy(psizegrid)
    p0.addGrid('labels','size','size')
    parsermap['/Pfeilpfad'] = [p0]

    # /Pfeilzahlen (edited: 24)
    p0 = copy.deepcopy(psizegrid)
    p0.removeProp('problem')
    p0.removeProp('solution')
    p0.addGrid('problem','size','size',lambda x:x+2,lambda x:x+2)
    p0.addGrid('solution','size','size',lambda x:x+2,lambda x:x+2)
    p1 = copy.deepcopy(p0)
    p1.removeProp('problem')
    p1.addGrid('problem','size','size')
    parsermap['/Pfeilzahlen'] = [p0,p1]

    # /Pillen
    p0 = copy.deepcopy(psizegrid)
    p0.removeProp('problem')
    p0.addGrid('problem','size','size',lambda x:x+1,lambda x:x+1)
    p1 = copy.deepcopy(prcgrid)
    p1.removeProp('problem')
    p1.addGrid('problem','rows','cols',lambda x:x+1,lambda x:x+1)
    parsermap['/Pillen'] = [p0,p1]

    # /Pipeline
    p0 = copy.deepcopy(prcgrid_labels1)
    p1 = copy.deepcopy(psizegrid_labels1)
    p0.setCommentChars(';') # 1-20 have lines starting with ;
    p1.setCommentChars(';')
    parsermap['/Pipeline'] = [p0,p1]

    # /Pipelink
    parsermap['/Pipelink'] = [psizegrid,prcgrid]

    # /Putteria
    parsermap['/Putteria'] = [psizegridareas,prcgridareas]

    # /Raitonanba
    parsermap['/Raitonanba'] = [psizegrid]

    # /Rechengitter
    p0 = copy.deepcopy(psizegrid)
    p0.removeProp('problem')
    # assume grid is lines until the "solution" property right after
    p0.addStrLong('problem',re.compile(r'^.*[^n]$'))
    p0.addNone('negative')
    parsermap['/Rechengitter'] = [p0]

    # /Reflect
    parsermap['/Reflect'] = [psizegrid,prcgrid]

    # /Regenwolken
    parsermap['/Regenwolken'] = [psizegrid]

    # /Rekuto
    parsermap['/Rekuto'] = [psizegrid]

    # /Renban
    parsermap['/Renban'] = [psizegridareas]

    # /Renkatsu
    parsermap['/Renkatsu'] = [psizegrid]

    # /Roma
    parsermap['/Roma'] = [psizegridareas]

    # /Rukkuea
    parsermap['/Rukkuea'] = [psizegrid]

    # /Rundreise (edited: 5)
    parsermap['/Rundreise'] = [psizegrid,prcgrid]

    # /Sashigane (edited: 20,60)
    parsermap['/Sashigane'] = [psizegrid,prcgrid]

    # /Sashikabe
    parsermap['/Sashikabe'] = [psizegrid]

    # /Satogaeri
    parsermap['/Satogaeri'] = [psizegridareas]

    # /Schlange
    parsermap['/Schlange'] = [psizegrid_labels1]

    # /Schlange/Akkara
    p0 = copy.deepcopy(psizegrid)
    p0.addStr('nlabels')
    parsermap['/Schlange/Akkara'] = [p0]

    # /Schlange/Knight
    parsermap['/Schlange/Knight'] = parsermap['/Schlange/Akkara']

    # /Schlangenlinie
    parsermap['/Schlangenlinie'] = [prcgrid,psizegrid]

    # /Scrin
    parsermap['/Scrin'] = [psizegrid,prcgrid]

    # /Seek-Numbers (deleted: 13,14)
    parsermap['/Seek-Numbers'] = [prcgrid]

    # /Serpentominos
    parsermap['/Serpentominos'] = [prcgrid]

    # /Shakashaka
    parsermap['/Shakashaka'] = [psizegrid,prcgrid]

    # /Shimaguni
    parsermap['/Shimaguni'] = [psizegridareas]

    # /Shingoki
    parsermap['/Shingoki'] = [psizegrid]

    # /Shirokuro
    parsermap['/Shirokuro'] = [psizegrid]

    # /Shugaku
    parsermap['/Shugaku'] = [psizegrid,prcgrid]

    # /Sikaku
    parsermap['/Sikaku'] = [prcgrid,psizegrid]

    # /Slitherlink
    parsermap['/Slitherlink'] = [prcgrid,psizegrid]

    # /Snake-Pit
    parsermap['/Snake-Pit'] = [psizegrid,prcgrid]

    # /Spotlight
    parsermap['/Spotlight'] = [psizegrid]

    # /Spukschloss (edited: 10)
    p0 = copy.deepcopy(psizegrid)
    p0.removeProp('problem')
    p0.addGrid('problem','size','size',lambda x:x+2,lambda x:x+2)
    p0.addInt('ghosts')
    p0.addInt('zombies')
    p0.addInt('vampires')
    p1 = copy.deepcopy(prcgrid)
    p1.removeProp('problem')
    p1.addGrid('problem','rows','cols',lambda x:x+2,lambda x:x+2)
    p1.addInt('ghosts')
    p1.addInt('zombies')
    p1.addInt('vampires')
    parsermap['/Spukschloss'] = [p0,p1]

    # /SquarO
    parsermap['/SquarO'] = [psizegrid]

    # /Sternenhaufen
    parsermap['/Sternenhaufen'] = [psizegrid]

    # /Sternenhimmel (edited: 25)
    parsermap['/Sternenhimmel'] = [psizegrid_labels1,prcgrid_labels1]

    # /Sternennacht (edited: 26)
    parsermap['/Sternennacht'] = [prcgrid_labels1]

    # /Sternenschlacht
    parsermap['/Sternenschlacht'] = [psizegridareas]

    # /Stitches (edited: 2)
    parsermap['/Stitches'] = [psizegridareas_labels1]

    # /Stostone
    parsermap['/Stostone'] = [psizegridareas,prcgridareas]

    # /Straights (edited: 5,463)
    parsermap['/Straights'] = [psizegrid]

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

    # /Sudoku/2D
    parsermap['/Sudoku/2D'] = [psizegrid]

    # /Sudoku/Butterfly
    parsermap['/Sudoku/Butterfly'] = [psizegrid]

    # /Sudoku/Chaos
    parsermap['/Sudoku/Chaos'] = [psizegridareas]

    # /Sudoku/Clueless-1
    parsermap['/Sudoku/Clueless-1'] = [psizegrid]

    # /Sudoku/Clueless-2
    parsermap['/Sudoku/Clueless-2'] = [psizegrid]

    # /Sudoku/Flower
    parsermap['/Sudoku/Flower'] = [psizegrid]

    # /Sudoku/Gattai-8
    parsermap['/Sudoku/Gattai-8'] = [prcgrid]

    # /Sudoku/Killer
    p0 = copy.deepcopy(psizegridareas)
    ppu.addParamsPattern(p0)
    p1 = copy.deepcopy(prcgridareas)
    ppu.addParamsPattern(p1)
    parsermap['/Sudoku/Killer'] = [p0,p1]

    # /Sudoku/Konsekutiv
    parsermap['/Sudoku/Konsekutiv'] = [psizegrid]

    # /Sudoku/Kropki
    p0 = copy.deepcopy(psizegrid)
    ppu.addParamsPattern(p0)
    parsermap['/Sudoku/Kropki'] = [p0]

    # /Sudoku/Magic-Number
    p0 = copy.deepcopy(psizegrid)
    p0.addGrid('clues','size','size')
    p0.addInt('magic')
    parsermap['/Sudoku/Magic-Number'] = [p0]

    # /Sudoku/Odd-Even
    parsermap['/Sudoku/Odd-Even'] = [psizegrid]

    # /Sudoku/Randsummen (edited: 94)
    p0 = copy.deepcopy(psizegrid)
    ppu.addParamsPattern(p0)
    parsermap['/Sudoku/Randsummen'] = [p0]

    # /Sudoku/Samurai
    parsermap['/Sudoku/Samurai'] = [psizegrid]

    # /Sudoku/Shogun
    parsermap['/Sudoku/Shogun'] = [prcgrid]

    # /Sudoku/Sohei
    parsermap['/Sudoku/Sohei'] = [psizegrid]

    # /Sudoku/Sumo
    parsermap['/Sudoku/Sumo'] = [psizegrid]

    # /Sudoku/Vergleich
    p0 = copy.deepcopy(psizegrid)
    ppu.addParamsPattern(p0)
    p0.addGrid('clues','size','size')
    parsermap['/Sudoku/Vergleich'] = [p0]

    # /Sudoku/Windmill
    parsermap['/Sudoku/Windmill'] = [psizegrid]

    # /Sudoku/Wolkenkratzer
    parsermap['/Sudoku/Wolkenkratzer'] = [psizegrid]

    # /Sudoku-Cup (moved: all)

    # /Sudoku-Kropki
    parsermap['/Sudoku-Kropki'] = parsermap['/Sudoku/Kropki']

    # /Sudoku-Odd-Even
    parsermap['/Sudoku-Odd-Even'] = parsermap['/Sudoku/Odd-Even']

    # /Sudoku-Randsummen (edited: 94)
    parsermap['/Sudoku-Randsummen'] = parsermap['/Sudoku/Randsummen']

    # /Sudoku-Varianten (moved: all)

    # /Suguru
    parsermap['/Suguru'] = [psizegridareas]

    # /Sukaku
    parsermap['/Sukaku'] = [psizegrid,psizegridareas]

    # /Sukano
    p0 = copy.deepcopy(psizegrid)
    p0.addGrid('rlabels','size','size',flags='s')
    p0.addGrid('clabels','size','size',flags='s')
    parsermap['/Sukano'] = [p0]

    # /Sukima
    parsermap['/Sukima'] = [psizegrid]

    # /Sukoro
    parsermap['/Sukoro'] = [psizegrid]

    # /Sukrokuro
    parsermap['/Sukrokuro'] = [psizegrid]

    # /Sumdoku
    parsermap['/Sumdoku'] = [psizegridareas]

    # /Suraido
    parsermap['/Suraido'] = [psizegrid]

    # /Suraromu
    parsermap['/Suraromu'] = [psizegrid,prcgrid]

    # /Symbolrechnen
    p0 = copy.deepcopy(prcgrid)
    p0.removeProp('problem')
    p0.removeProp('solution')
    p0.addStrLong('problem',re.compile(r'^.*[^n]$')) # until "solution" line
    p0.addStrLong('solution',re.compile(r'^.*[^sd]$')) # until "moves" line or "end" line
    parsermap['/Symbolrechnen'] = [p0]

    # /Tairupeinto
    parsermap['/Tairupeinto'] = [psizegridareas_labels1]

    # /Tapa
    parsermap['/Tapa'] = [psizegrid,prcgrid]

    # /Tapa/1-to-N
    parsermap['/Tapa/1-to-N'] = [psizegrid]

    # /Tapa/Islands
    parsermap['/Tapa/Islands'] = [psizegrid]

    # /Tapa-Varianten (moved: all)

    # /Tapa/Yin-Yang
    parsermap['/Tapa/Yin-Yang'] = [psizegrid]

    # /Tasukuea (edited: 8)
    parsermap['/Tasukuea'] = [psizegrid]

    # /Tatamibari
    parsermap['/Tatamibari'] = [psizegrid]

    # /Tateboo-Yokoboo
    parsermap['/Tateboo-Yokoboo'] = [psizegrid,prcgrid]

    # /Terra-X
    parsermap['/Terra-X'] = [psizegridareas]

    # /Tetroid
    parsermap['/Tetroid'] = [psizegrid]

    # /Thermometer
    p0 = copy.deepcopy(psizegrid_labels1)
    p0.addGrid('labels','size','size')
    parsermap['/Thermometer'] = [p0]

    # /Tohu-Wa-Vohu
    parsermap['/Tohu-Wa-Vohu'] = [psizegrid]

    # /Toichika
    parsermap['/Toichika'] = [psizegridareas]

    # /Trace-Numbers
    parsermap['/Trace-Numbers'] = [prcgrid]

    # /Trilogik
    parsermap['/Trilogik'] = [psizegrid]

    # /Trinudo
    parsermap['/Trinudo'] = [psizegrid]

    # /Tripletts
    parsermap['/Tripletts'] = [prcgridareas,psizegridareas]

    # /Tueren
    parsermap['/Tueren'] = [psizegrid]

    # /Usoone (edited: 51)
    parsermap['/Usoone'] = [psizegridareas]

    # /Usotatami
    parsermap['/Usotatami'] = [psizegrid]

    # /Varianten (moved: all)

    # /Vier-Winde
    parsermap['/Vier-Winde'] = [psizegrid]

    # /View
    parsermap['/View'] = [psizegrid]

    # /Wasserspass (edited: 3)
    p0 = copy.deepcopy(psizegrid_labels1)
    p0.addGrid('lines','size','size')
    p1 = copy.deepcopy(prcgrid_labels1)
    p1.addGrid('lines','rows','cols')
    parsermap['/Wasserspass'] = [p0,p1]

    # /Wolkenkratzer (edited: 410) (first puzzle in 410 is broken)
    parsermap['/Wolkenkratzer'] = [psizegrid_labels2]

    # /Wolkenkratzer-2
    parsermap['/Wolkenkratzer-2'] = [psizegrid_labels2]

    # /Yagit
    parsermap['/Yagit'] = [psizegrid]

    # /Yajikabe
    parsermap['/Yajikabe'] = [psizegrid]

    # /Yajilin
    parsermap['/Yajilin'] = [psizegrid,prcgrid]

    # /Yajilin-Regional
    parsermap['/Yajilin-Regional'] = [psizegridareas,prcgridareas]

    # /Yajisan-Kazusan (moved: Inverted,Liar,Liar-Arrows,No-2x2,Odd,Off-By-One)
    parsermap['/Yajisan-Kazusan'] = [psizegrid,prcgrid]

    # /Yakuso
    parsermap['/Yakuso'] = [psizegrid,prcgrid]

    # /Yin-Yang
    parsermap['/Yin-Yang'] = [psizegrid]

    # /Yonmasu
    parsermap['/Yonmasu'] = [psizegrid]

    # /Yosenabe
    parsermap['/Yosenabe'] = [psizegridareas]

    # /Zahlenkreuz
    parsermap['/Zahlenkreuz'] = [psizegrid_labels1]

    # /Zahlenlabyrith (edited: 1)
    p0 = copy.deepcopy(psizegrid)
    p0.addGrid('lines','size','size')
    parsermap['/Zahlenlabyrinth'] = [p0]

    # /Zahlenschlange
    parsermap['/Zahlenschlange'] = [psizegrid]

    # /Zehnergitter
    parsermap['/Zehnergitter'] = [prcgrid]

    # /Zeltlager
    parsermap['/Zeltlager'] = [psizegrid,prcgrid]

    # /Zeltlager-2
    parsermap['/Zeltlager-2'] = [psizegrid]

    # /Ziegelmauer
    p0 = copy.deepcopy(psizegrid)
    p0.addStr('areas')
    parsermap['/Ziegelmauer'] = [p0]

    # /Zipline
    parsermap['/Zipline'] = [prcgrid]

    # /Zitatemix
    p0 = copy.deepcopy(prcgrid)
    p0.removeProp('solution')
    p0.addStrLong('solution',re.compile(r'^.+...$')) # lines with >= 4 chars
    parsermap['/Zitatemix'] = [p0]

    # /Zwischenknick
    parsermap['/Zwischenknick'] = [psizegrid]

createParsers()

# check if parsers are missing
if 1:
    for dirpath,dirnames,filenames in os.walk(base_dir):
        puzzle_path = dirpath[len(base_dir):]
        if puzzle_path in parsermap:
            #print('in parsermap:',puzzle_path)
            if len(filenames) == 0:
                print('remove from parsermap:',puzzle_path)
                #break
            #assert len(filenames) > 0
        else:
            #print('NOT in parsermap:',puzzle_path)
            if len(filenames) > 0:
                print('add to parsermap:',puzzle_path)
                #break
            elif puzzle_path not in noparserlist:
                print('add to noparsermap:',puzzle_path)
            #assert len(filenames) == 0

def main(puzzle: str, out_file: str):
    #puzzle = sys.argv[1]
    #out_file = sys.argv[2]
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
    if len(failed_files) > 0:
        assert 0

if __name__ == '__main__':
    if len(sys.argv) > 2:
        main(sys.argv[1],sys.argv[2])
    elif sys.argv[1] == 'all':
        for puzzle in parsermap:
            #print(puzzle,'->','../puzzle_jsonl/'+puzzle[1:].replace('/','_')+'.jsonl')
            main(puzzle,'../puzzle_jsonl/'+puzzle[1:].replace('/','_')+'.jsonl')
    #for puzzle in parsermap:
    #    main(puzzle,'/dev/null')

