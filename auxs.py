
import os
import time
import numpy as np
import shutil
from pathlib import Path



# only valid for steps for now
def get_steps_vals(points):
    cxs = 0
    for i in range(len(points)-1):
        if points[i+1] - points[i] > 0.01:
            cxs.append([i, pos[i]])
    return cxs

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
    data_points = [float(px[2:]) for px in pxs if px.startswith('\t')]
    return data_points

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

# simple window menu (returns None if quit)
# TODO: maybe not os.chdir but point to it?
def file_menu(path='',file_ext=[]):
    if path:
        try:
            os.chdir(path)
        except:
            print(f'\ncould\'t open: {path}')
    mistake = False
    while True:
        if mistake:
            print('\ninvalid option')
            mistake = False
        cwd = os.getcwd()
        print(f'\ncurrent location: {cwd}')
        print(f'current file extension: {file_ext}')
        if type(file_ext) == str:
            entries = [i for i in os.listdir() if i.endswith(file_ext)]
        elif type(file_ext) == list:
            entries = []
            for fe in file_ext:
                entries += [i for i in os.listdir() if i.endswith(file_ext)]
        else:
            print(f'unrecognized type of file extension: {file_ext} (can be str or list)')
        entries += [i for i in os.listdir() if os.path.isdir(i) and i not in entries]
        entries.sort()
        print()
        for ei,entry in enumerate(entries):
            print(f'{ei+1} - {entry}')
        print('[u] to go up a directory')
        print('[f] to change file extension')
        print('[q] to quit (returns None)')
        xi = input("\n >> ")
        if xi == 'q' or xi == 'quit':
            return
        elif xi == 'f':
            file_ext = input('\nnew file extension >> ')
            print(f'new file ext: {file_ext}')
        elif xi == 'u' or xi == 'up':
            os.chdir('..')
        else:
            try:
                fname = entries[int(xi)-1]
                print(f'\nselected: {fname}')
            except:
                mistake = True
            if not mistake:
                if os.path.isdir(fname):
                    os.chdir(os.path.join(cwd,fname))
                else:
                    return fname

# simple de-interleave
def deinterleave(stack):
    ch1 = stack[0::2]
    ch2 = stack[1::2]
    return ch1,ch2

# raw way to look inside methods of an object
# in_name assumes names separated by '_'
def check_methods(object, in_name=''):
    # filter some methods
    for mx in dir(object):
        mxs = []
        if type(in_name) == str and in_name != '':
            if in_name in mx.split('_'):
                mxs.append(mx)
        else:
            mxs.append(mx)
    # check if possible
    for mx in mxs:
        print()
        print(mx)
        try:
            x = getattr(object,mx)
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
