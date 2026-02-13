
import os
import time
import numpy as np
import shutil
from pathlib import Path
import platform
from collections import defaultdict
import tifffile as tf
import re



# make shorter arr into the same size as the larger by copying (tiling)
# returns in the same order as received
def tile2arr2(arr1,arr2):
    if arr1.size > arr2.size:
        f = int(arr1.size/arr2.size) + 1
        arr2e = np.tile(arr2, f)
        arr2e = arr2e[:arr1.size]
        return arr1, arr2e
    else:
        f = int(arr2.size/arr1.size) + 1
        arr1e = np.tile(arr1, f)
        arr1e = arr1e[:arr2.size]
        return arr1e, arr2

# split path into dir & file
def get_dir_file_paths(fpath):
    if not os.path.isfile:
        raise Exception(f'{fpath} is not a file')
    sep = '\\' if platform.system() == 'Windows' else '/'
    sp = fpath.split(sep)
    fname = sp[-1]
    dirpath = sep.join(sp[:-1])
    return dirpath, fname

# change extension
def change_extension(fname,new_ext):
    basename = fname.split('.')[0]
    if not new_ext:
        return basename
    return f'{basename}.{new_ext}'

# search for file with some ext or tag in the same folder as another file
# as_list returns data as list, be it 0, 1 or many
# tag assumes separation usgin underscores
def search_in_filedir(fpath,ext='',tag='',as_list=False):
    sep = '\\' if platform.system() == 'Windows' else '/'
    fdir = sep.join(fpath.split(sep)[:-1])
    files = [os.path.join(fdir,x) for x in os.listdir(fdir) if x.endswith(str(ext))]
    if tag:
        tag_files = []
        for file in files:
            if tag in file.split('_'):
                tag_files.append(file)
        files = tag_files
    if as_list:
        return files
    files = files[0] if len(files) > 0 else ''
    return files

# save in the same folder of fpath
def mk_savepath(fpath,ext='',tag=''):
    sep = '\\' if platform.system() == 'Windows' else '/'
    fdir = sep.join(fpath.split(sep)[:-1])
    name, oext = fpath.split(sep)[-1].split('.')
    # if different extension
    ext = ext if ext else oext
    # if extra tag
    tag = f'_{tag}' if tag else ''
    # mk savepath
    fname = f'{name}{tag}.{ext}'
    savepath = os.path.join(fdir,fname)
    # to avoid overwrite or crashing
    if os.path.isfile(savepath):
        now = time.time()
        sname, sext = savepath.split('.')
        savepath = f'{sname}_{now}.{sext}'
    return savepath

# makes a dictionary with info from every slice about some tag
def get_medata_from_tif(tif_file_path,tag='ImageDescription'):
    tif = tf.TiffFile(tif_file_path)
    # print for info
    print(f'currently using tag={tag}. Other tags are:')
    for tx in tif.pages[0].tags.values():
        print(tx.name)
    # there are different tags, I'm only getting this for now
    raw_info = [page.tags[tag].value for page in tif.pages]
    # parse
    tag_info = defaultdict(list)
    for page in raw_info:
        for x in page.split('\r'):
            key,value = x.split('=')
            tag_info[key] += value
    return tag_info

# converts list of (start, end) to indices for np arrays
def mk_np_indexes(indexes):
    return np.concatenate([np.arange(a,b) for a,b in indexes])

# just print some wave data
def print_wave_data(wave):
    print('\nwave header')
    for k,v in wave['wave_header']:
        print(f'{k}: {v}')
    print('\nnote:')
    for x in wave['note'].decode(errors='replace').split('\r'):
        print(x)

# just read and returns data points from the .itx file
def read_itx(fpath_itx):
    if os.path.isfile(fpath_itx) and fpath_itx.endswith('itx'):
        p = Path(fpath_itx)
        # replaces invalid chars with unicode repl char: '?'
        # the 'ignore' option just removes them, but this safeguards structure
        itx_data = p.read_text(errors='replace')
    else:
        raise '\nit isn\'t an .itx file\n'
    li = itx_data.split(',')
    pxs = li[0].split('\n')
    data_points = np.array([float(px[2:]) for px in pxs if px.startswith('\t')])
    return data_points

# check path for loading (dir or file)
def check_file_dir(path):
    if os.path.isfile(path):
        return path
    if os.path.isfile(os.path.join(os.getcwd(),path)):
        return os.path.join(os.getcwd(),path)
    if os.path.isidr(path):
        return path

# look for dir in folders (going up only)
def dir_upsearch(dirname, filename=None, verbose=False):
    for i in range(5):
        cdir = os.path.abspath('../'*i)
        if verbose:
            print(f'looking in: {cdir}')
        if dirname in os.listdir(cdir):
            fpath = os.path.join(cdir,dirname)
            print(os.listdir(fpath))
            if filename and filename in os.listdir(fpath):
                if verbose:
                    print(os.listdir())
                fpath = os.path.join(fpath,filename)
            if verbose:
                print(fpath)
            return fpath
    return os.getcwd()

# to convert a string of items into a list of arguments
def string_as_list(string):
    # check if commas + spaces
    if ', ' in string:
        string.replace(',',' ')
    return string.split(',')
    # check if sepparated only by commas (no spaces)
    if ',' in string:
        return string.split(',')
    # else (as it is)
    return [string]
    

# simple de-interleave
def deinterleave(stack):
    ch1 = stack[0::2]
    ch2 = stack[1::2]
    return ch1,ch2

# raw way to look inside methods of an object
# in_name assumes names separated by '_'
def inspect_methods(object, in_name='',startswith='',endswith=''):
    # filter some methods (optional, otherwise it will include all)
    mxs = []
    for method in dir(object):
        if method.startswith(str(startswith)):
            mxs.append(method)
        elif method.endswith(str(endswith)):
            mxs.append(method)
        elif re.search(str(in_name),method):
            mxs.append(method)
    # check if possible
    for mx in mxs:
        print()
        print(mx)
        try:
            x = getattr(object,mx)
            print(f'{mx}: {x}')
        except:
            print(x)
            print('prob require args')

# for windows temp handling issue
def rmtree_retry(path, tries=30, delay=0.1):
    for i in range(tries):
        try:
            shutil.rmtree(path)
            return
        except PermissionError:
            time.sleep(delay)
    # last try (raise if still locked)
    shutil.rmtree(path)



























#
