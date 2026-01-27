
import os
import time
import numpy as np
import shutil
from pathlib import Path
from igor2 import packed
import platform
from collections import defaultdict
import tifffile as tf

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






# wrapper for loading imaging data
def load_stimulus_response(path):
    # try to find correct path
    fpath = None
    # if path = full path
    if os.path.isfile(str(path)) and path.endswith('.pxp'):
        fpath = path
    # if path = dir
    elif os.path.isdir(str(path)):
        for filename in os.listdir(path):
            if filename.endswith('.pxp'):
                fpath = os.path.join(path,filename)
                break
    # if path = filename (with/without extension)
    else:
        # look in current dir
        for filename in os.listdir(os.getcwd()):
            if filename == path or filename.split('.')[0] == path:
                fpath = os.path.join(os.getcwd(),filename)
    # try to load igor exp
    if fpath:
        print(f'\ntrying to load .pxp file at {fpath}\n')
        try:
            rx_wave, reg_wave, sti_wave = load_waves_from_igor_exp(fpath)
            # transpose axes: [time][y][x] => [t][row][col]
            response = rx_wave['wData'].T
            response_reg = reg_wave['wData'].T
            stimulus = sti_wave['wData']
            stimulus = stimulus/10**6 if stimulus.mean() > 100 else stimulus
            return response, response_reg, stimulus
        except:
            print('\nexperiment too complex for igor2 module\n')
    else:
        print('\nno experiment found\n')
    # try to load from files in folder
    # if path = full path
    if os.path.isfile(str(path)) and (path.endswith('.tif') or path.endswith('.tiff')):
        fpath = path
    # if path = dir, look for tif/tiff files inside
    elif os.path.isdir(str(path)):
        # look for reg file
        for filename in os.listdir(str(path)):
            if filename.endswith('.tif') or filename.endswith('tiff'):
                if 'reg' in file.split('_'):
                    fpath = file
                    break
        # if no reg file
        if not fpath:
            # in case there's more than one
            tif_files = []
            for filename in os.listdir(path):
                # check if stack and not an image (im size ~ 215 kb for 1 frame)
                # also discard temporal frequency files
                if os.stat(filename).st_size()/1024 > 5000 and filename.lower().startswith('tf'):
                    tif_files.append(os.path.join(path,filename))
            # easy choice
            if len(tif_files) == 1:
                fpath = tif_files[0]
            # otherwise just get the heavier 'step' one assuming is the raw file
            if not fpath:
                tif_files = [[i,os.stat(i).st_size] for i in tif_files].sort(key=lambda x:x[1], reverse=True)
                fpath = tif_files[0] if len(tif_files) > 0 else None
    # if path = filename (with/without extension)
    else:
        # look for file in current dir
        for filename in os.listdir(os.getcwd()):
            if filename == path or filename.split('.')[0] == path:
                    fpath = os.path.join(os.getcwd(),filename)
    # if nothing worked, open file menu
    if not fpath:
        fpath = file_menu(dirpath, file_ext='tif,tiff,pxp')
    # TODO: same code as above - make fx
    # if igor exp
    if os.path.isfile(str(path)) and ends.endswith('.pxp'):
        print(f'\ntrying to load .pxp file at {fpath}\n')
        try:
            rx_wave, reg_wave, sti_wave = load_waves_from_igor_exp(fpath)
            # transpose axes: [time][y][x] => [t][row][col]
            response = rx_wave['wData'].T
            response_reg = reg_wave['wData'].T
            stimulus = sti_wave['wData']
            stimulus = stimulus/10**6 if stimulus.mean() > 100 else stimulus
            return response, response_reg, stimulus
        except:
            print('\nexperiment too complex for igor2 module\n')
            fpath = None
    elif fpath:
        # if tif file: try to load tiff & itx files from folder
        response, response_reg, stimulus = None, None, None
        # opt1: (response_reg + .itx file)
        # opt2: response (raw): ch1 => response_reg, ch2 => stimulus (if needed)
        print('\ntryng to load individual files from folder\n')
        print(f'stack: {fpath}')
        # if de-interleaved & registered; response = None
        try:
            if 'reg' in fpath.split('_'):
                response_reg = tf.imread(fpath)
                print(f'loaded registered stack at {fpath}')
            else:
                # otherwise, raw stack
                response = tf.imread(fpath)
                print(f'loaded raw stack at {fpath}')
        except:
            print(f'\ncouldn\'t load stack at {fpath}\n')
            fpath = None
        # if tiff
        if (fpath and response) or (fpath and response_reg):
            # load itx file with stimulus data, assuming same folder
            sep = '\\' if platform.system() == 'Windows' else '/'
            exp_path = sep.join(fpath.split(sep)[:-1])
            itxs = [x for x in os.listdir(exp_path) if x.endswith('.itx')]
            fname_itx = itxs[0] if len(itxs) > 0 else None
            if fname_itx:
                fpath_itx = os.path.join(exp_path,fname_itx)
                print(f'loading .itx file for stimulus: {fpath_itx}')
                try:
                    stimulus = read_itx(fpath_itx)
                    print(f'ok')
                except:
                    print(f'\ncouldn\'t load .itf file at {fpath_itx}\n')
        # check if opt1 (i.e. return raw reponse = None)
        if response_reg and stimulus:
            return response, response_reg, stimulus
        # check if raw response + stimulus
        if response:
            # de-interleave & register
            response, ch2 = deinterleave(response)
            # TODO: register in Igor
            print('registering raw stack with caiman')
            response_reg = caiman_reg(response)
            # check stimulus
            if stimulus:
                return response, response_reg, stimulus
            # TODO
            try:
                itx_path = mk_itx_file(ch2)
            except:
                print('\ncouldn\'t make stimulus file calling Igor\n')
                fpath = None
    else:
        print('\nNo file to load...\n')

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
