# janko.at puzzle scraping

There is a nice collection of a wide variety of logic puzzles at
https://janko.at/Raetsel/. These puzzles are on individual pages in a machine
readable format. For logic puzzle project ideas and research, having a
collection of puzzles can be very helpful. The goal here is to collect puzzles
in bulk from this website and store them as JSONL files (1 JSON object per line)
that would help me with some project ideas by removing some of the complexity of
parsing. The website gets regularly updated with new puzzles so this repository
will likely be out of date.

The web pages with puzzles have a data element describing the puzzle, such as:
```html
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
```

In the end, there will be a JSONL file per type of puzzle (such as Sudoku). Each
line will represent 1 puzzle as `{"file":"/Sudoku/0001.a.x-janko","data":DATA}`,
where `DATA` is a JSON representation of the puzzle data extracted from the web
page.

The `PuzzleParser.py` file has a class for defining a parser that can parse the\
puzzle by iterating the lines. The `PuzzleParserUtils.py` file has some
functionality to simplify defining parsers that share several similarities.

The puzzle data (that which would be in place of `DATA` as described) has some
inconsistencies that complicate parsing. Sometimes, multiple parsers need to be
defined to successfully parse all puzzles in a directory. The parsing code may
not be perfect, but it is designed to minimize the amount of manual editing to
fix inconsistencies and fail/error when there is an issue. The `.x-janko` files
can be edited manually where necessary, but this is tedious and should be done
as little as reasonably possible.

The `parse_data.py` script takes the puzzle path (relative to `/Raetsel` on the
server) and a file to write the JSONL data to. This only produces JSON
representations of the puzzles. Checking the validity of these puzzles is out of
the scope of this project and probably something that can be done one puzzle at
a time for further use.

# instructions

Note: all paths are relative to the root of this repository.

1. Run `./download_site.sh` to save the website to `www.janko.at` using `wget`.
2. Run `python3 ./parser/extract_data.py` to extract the data portion from the
web pages and store then as `.x-janko` files (containing text) in
`puzzle_x-janko`. This part should run smoothly since there was no issue with
parsing the web pages as of May 2022.
3. Run `python3 ./parser/parse_data.py <PUZZLE> <FILE>` to convert all of a
puzzle type to a JSONL file. Due to inconsistencies in the puzzle data, this
step may produce errors and require defining parsers or manually editing the
`.x-janko` files to complete successfully. The puzzle is specified as a path
relative to `/Raetsel` on the server, such as `/Sudoku` and the output file can
be anything, preferably with the `.jsonl` extension.
