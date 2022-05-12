'''
Attempts to download puzzle files that may have been missed in the main wget
website download. This script goes through all the x-janko file directories and
tries to download higher numbered puzzles (or starting from 1 if there are none)
in order to collect missing puzzles.

For example, Area-51 puzzles 1-9 are downloaded by wget but 10-20 have pages on
the site that are not downloaded since it appears they are not linked anywhere.

Many puzzles have an additional 10 (or maybe 20) that are not linked anywhere,
thus missed my the wget command.
'''

import bs4
import os
import re
import requests
import sys
from typing import List, Set

local_base_dir = os.path.normpath('../puzzle_x-janko/')
remote_base_dir = os.path.normpath('janko.at/Raetsel/')

fname_re = re.compile(r'^\d\d\d\d?.a.x-janko$')
extra_tries = 3 # number of attempts past highest numbered puzzle

if __name__ == '__main__':

    dl_paths = sys.argv[1:]

    for dirpath,dirnames,filenames in os.walk(local_base_dir):
        path = dirpath.replace(local_base_dir,'',1)
        remote_dir = 'https://'+remote_base_dir+path
        if dl_paths and path not in dl_paths:
            continue
        print('processing dir: '+path)
        print('remote: '+remote_dir)
        print('found %d files'%len(filenames))
        filenames = sorted(filenames)
        puzzle_nums: Set[int] = set() # puzzle numbers found
        for filename in filenames:
            if fname_re.match(filename):
                puzzle_num = int(filename.split('.')[0])
                if puzzle_num in puzzle_nums:
                    print('WARN: duplicate puzzle number: %d'%puzzle_num)
                puzzle_nums.add(puzzle_num)
            else:
                print('WARN: irregular filename: '+filename)
        if puzzle_nums:
            max_puzzle_num = max(puzzle_nums)
        else:
            max_puzzle_num = 0
        print('max puzzle num: %d'%max_puzzle_num)
        puzzle_num_limit = max_puzzle_num+extra_tries
        puzzle_num = 0
        while puzzle_num < puzzle_num_limit:
            puzzle_num += 1
            if puzzle_num in puzzle_nums: # already saved
                continue
            print('attempting to download %d...'%puzzle_num)
            # try 4 digit url first
            # if 3 digit urls are still accessible, it appears they were just
            # copied to the 4 digit url when there are >= 1000 of the puzzle
            urls: List[str] = [remote_dir+'/%04d.a.htm'%puzzle_num]
            urls.append(remote_dir+'/%03d.a.htm'%puzzle_num)
            if urls[0] == urls[1]:
                urls = urls[:1]
            success = False
            for url in urls:
                request = requests.get(url)
                if not request.ok:
                    continue
                page = bs4.BeautifulSoup(request.text,'html.parser')
                data = page.find(id='data')
                if data is None:
                    continue
                elif isinstance(data,bs4.Tag):
                    assert data.attrs['type'] == 'application/x-janko'
                    data = data.string
                    assert data is not None
                    out_data = '\n'.join(data.splitlines())+'\n'
                    page_name = os.path.split(url)[1]
                    out_file = local_base_dir+path+'/'+os.path.splitext(page_name)[0]+'.x-janko'
                    outf = open(out_file,'w')
                    outf.write(out_data)
                    outf.close()
                    success = True
                    print('successful from url: '+url)
                    puzzle_num_limit = max(puzzle_num_limit,puzzle_num+extra_tries)
                    break
                else:
                    assert 0
            if not success:
                print('WARN: failure')
        print()

