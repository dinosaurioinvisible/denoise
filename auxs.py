
import os
import time
import numpy as np
import shutil
from pathlib import Path
from igor2 import packed
import platform
from collections import defaultdict
import tifffile as tf
import re

# TODO: igor2 only open 'simple' waves


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

# converts list of steps (start, end, value) into np indices
def steps2indexes(steps,val,base=False):
    if base:
        step_indexes = np.vstack((steps[0],steps[-1]))[:,:2]
    else:
        step_indexes = steps[np.where(steps[:,2]==val)][:,:2]
    import pdb; pdb.set_trace()
    np_indexes = mk_np_indexes(step_indexes)
    return np_indexes

# converts list of (start, end) to indices for np arrays
def mk_np_indexes(indexes):
    return np.concatenate([np.arange(a,b) for a,b in indexes])

# open igor exp - returns: registered response, stimulus
# if all_waves = True, returns list with [name, wave]
def load_waves_from_igor_exp(exp_path, all_waves=False, print_data=True):
    if os.path.isfile(exp_path) and exp_path.endswith('.pxp'):
        pxp = packed.load(exp_path)
        # pxp is a tuple: [0]: list of records, [1]: dict['root']
        print('\nIgor waves in experiment:')
        if all_waves:
            waves = []
        stimulus = None
        for key,v in pxp[1]['root'].items():
            # igor2 loads WaveRecords object containing byte_order, data, header & wave
            # wave is a dict with 2 keys 'version' & 'wave' (also dict)
            # i'm only loading wave here (data seems to be the same encoded as bytes)
            if 'wave' in str(type(v)).split('.'):
                k = key.decode()
                # import pdb; pdb.set_trace()
                print(k)
                if k.endswith('Ch1'):
                    response = v.wave['wave']
                    print(f'response = {k}')
                    if print_data:
                        print_wave_data(response)
                if k.endswith('Ch1_reg'):
                    response_reg = v.wave['wave']
                    print(f'response_reg = {k}')
                    if print_data:
                        print_wave_data(response_reg)
                if k.endswith('timewave'):
                    stimulus = v.wave['wave']
                    print(f'stimulus = {k}')
                    if print_data:
                        print_wave_data(stimulus)
                if all_waves:
                    waves.append([k,v.wave['wave']])
        # wave keys: bin_header, wave_header, wData (array), formula,
        # note (metadata), data_units, dimension_units, labels, sIndices
        if all_waves:
            return waves
        return response, response_reg, stimulus
    else:
        print('\nno .pxp file at path {path}\n')

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

# just print some wave data
def print_wave_data(wave):
    print('\nwave header')
    for k,v in wave['wave_header']:
        print(f'{k}: {v}')
    print('\nnote:')
    for x in wave['note'].decode(errors='replace').split('\r'):
        print(x)

# for steps experiments in Igor
def get_steps_vals(points,delta=0.1):
    cxs = []
    for i in range(len(points)-1):
        if abs(points[i+1] - points[i]) > delta:
            cxs.append([i, points[i+1]])
    steps = []
    for i in range(len(cxs)-1):
        steps.append([cxs[i][0]+1, cxs[i+1][0], cxs[i][1]])
    last_i = cxs[-1][0]+1
    steps.append([last_i, len(points), points[last_i]])
    return np.array(steps).astype(int)

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

# simple window menu (returns None if quit)
# TODO: maybe not os.chdir but point to it?
def file_menu(path='',file_ext=['']):
    # im hardocing this for now
    if not path:
        if platform.system() == 'Windows':
            path = 'C:\\Users\\Fernando\\zf\\data'
        else:
            path = '/Users/f/Dropbox/_r66y/r66xe/2p_data/'
    # try to open menu in path
    try:
        os.chdir(path)
    except:
        print(f'\ncould\'t open: {path}')
        path = None
    mistake = False
    while True:
        # print at top
        if mistake:
            print('\ninvalid option')
            mistake = False
        if not path:
            path = os.getcwd()
        print(f'\ncurrent location: {path}')
        print(f'current file extension: {file_ext}')
        # enable file ext
        if type(file_ext) == str:
            entries = [i for i in os.listdir() if i.endswith(file_ext)]
        elif type(file_ext) == list:
            entries = []
            for fe in file_ext:
                entries += [i for i in os.listdir() if i.endswith(file_ext)]
            import pdb; pdb.set_trace()
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
