
import os
import time
import numpy as np
import shutil
from pathlib import Path
from igor2 import packed

# TODO: igor2 only open 'simple' waves


# converts list of steps (start, end, value) into np indices
def steps2indexes(steps,val,base=False):
    if base:
        step_indexes = np.vstack((steps[0],steps[-1]))[:,:2]
    else:
        step_indexes = steps[np.where(steps[:,2]==val)][:,:2]
    np_indexes = mk_np_indexes(step_indexes)
    return np_indexes

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

# open igor exp - returns: registered response, stimulus
# if all_waves = True, returns list with [name, wave]
def load_waves_from_igor_exp(exp_path, all_waves=False):
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
                if k.endswith('Ch1_reg'):
                    response_reg = v.wave['wave']
                    print(f'response_reg = {k}')
                if k.endswith('timewave'):
                    stimulus = v.wave['wave']
                    print(f'stimulus = {k}')
                if all_waves:
                    waves.append([k,v.wave['wave']])
        # wave keys: bin_header, wave_header, wData (array), formula,
        # note (metadata), data_units, dimension_units, labels, sIndices
        if all_waves:
            return waves
        return response, response_reg, stimulus
    else:
        print('\nno .pxp file at path {path}\n')

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
