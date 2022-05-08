'''
Extract puzzle data from .htm files.
'''

import bs4
import os
from tqdm import tqdm
from typing import List, Tuple

# wrapper for os.mkdir to ignore error if directory exists
def mkdir(dir):
    if not os.path.isdir(dir):
        os.mkdir(dir)

base_dir = os.path.normpath('../www.janko.at/Raetsel/')
out_dir = os.path.normpath('../puzzle_x-janko/')
ignore_types = ['.css','.gif','.jpg','.js','.png']

if __name__ == '__main__':

    mkdir(out_dir)
    # list of (puzzle,filepath)
    filelist: List[Tuple[str,str]] = []

    for dirpath,dirnames,filenames in os.walk(base_dir):
        dirpath = dirpath[len(base_dir):] if dirpath != base_dir else ''
        for f in filenames:
            filelist.append((dirpath,dirpath+'/'+f))
        htm_files = [f for f in filenames if f.endswith('.htm')]
        print('PATH='+dirpath+' (%d files, %d htm)'%(len(filenames),len(htm_files)))

    print('Found %d files'%len(filelist))

    for puzzle,filepath in tqdm(filelist):
        mkdir(out_dir+'/'+puzzle)
        out_file = out_dir+os.path.splitext(filepath)[0]+'.x-janko'
        ext = os.path.splitext(filepath)[1]
        # ignore certain types and already created output
        if ext in ignore_types:
            continue
        if os.path.isfile(out_file):
            continue
        tqdm.write('converting: '+base_dir+filepath+' -> '+out_file)
        if ext != '.htm' and ext != '.html':
            tqdm.write('WARN: unsupported type')
            continue
        with open(base_dir+filepath,'r') as file:
            page = bs4.BeautifulSoup(file,'html.parser')
            data = page.find(id='data')
            if data is None:
                tqdm.write('WARN: no "data" tag, skipping')
            elif isinstance(data,bs4.Tag):
                assert data.attrs['type'] == 'application/x-janko'
                data = data.string
                assert data is not None
                out_data = '\n'.join(data.splitlines())+'\n'
                outf = open(out_file,'w')
                outf.write(out_data)
                outf.close()
                tqdm.write('successful')
            else:
                assert 0

