

import os
# import time
import numpy as np
from igor2 import packed
import platform
# from collections import defaultdict
# import tifffile as tf
# from stack2stimulus import ch2stimulus
# from auxs import print_wave_data
from auxs import string_as_list


# wrapper for loading imaging data


# to load igor experiment
def load_pxp(path):
    # 1) try to find correct path for igor exp
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
    # if path = filename without extension
    else:
        # look in current dir
        for filename in os.listdir(os.getcwd()):
            if filename.split('.')[0] == path and filename.endswith('.pxp'):
                fpath = os.path.join(os.getcwd(),filename)
    if not fpath:
        print('\ncouldn\'t find .pxp\n')
        fpath = file_menu(ext='tif, tiff, pxp')
        return
    # 2) try to load igor exp
    if fpath:
        print(f'\ntrying to load .pxp file at {fpath}')
        try:
            rx_wave, reg_wave, sti_wave = load_waves_from_igor_exp(fpath)
            # transpose axes: [time][y][x] => [t][row][col]
            response = rx_wave['wData'].T
            response_reg = reg_wave['wData'].T
            stimulus = sti_wave['wData']
            stimulus = stimulus/10**6 if stimulus.mean() > 100 else stimulus
            return response, response_reg, stimulus
        except:
            print('experiment too complex for igor2 module')
            return


# open igor exp - returns: registered response, stimulus
# if all_waves = True, returns list with [name, wave]
def load_waves_from_igor_exp(exp_path, all_waves=False):
    response, response_reg, stimulus = None, None, None
    if os.path.isfile(exp_path) and exp_path.endswith('.pxp'):
        pxp = packed.load(exp_path)
        # pxp is a tuple: [0]: list of records, [1]: dict['root']
        print('\nIgor waves in experiment:')
        if all_waves:
            waves = []
        for key,v in pxp[1]['root'].items():
            # igor2 loads WaveRecords object containing byte_order, data, header & wave
            # wave is a dict with 2 keys 'version' & 'wave' (also dict)
            # i'm only loading wave here (data seems to be the same encoded as bytes)
            if 'wave' in str(type(v)).split('.'):
                k = key.decode()
                # import pdb; pdb.set_trace()
                print(k)
                if k.endswith('_Ch1'):
                    response = v.wave['wave']
                    print(f' --> response = {k}')
                if k.endswith('_Ch1_reg'):
                    response_reg = v.wave['wave']
                    print(f' --> response_reg = {k}')
                if k.endswith('timewave'):
                    stimulus = v.wave['wave']
                    print(f' --> stimulus = {k}')
                # in case there's no timewave 
                # TODO
                # if k.endswith('_Ch2'):
                #     ch2 = v.wave['wave']
                if all_waves:
                    waves.append([k,v.wave['wave']])
        # wave keys: bin_header, wave_header, wData (array), formula,
        # note (metadata), data_units, dimension_units, labels, sIndices
        if all_waves:
            return waves
        if not response:
            raise Exception('error: no Ch1 response wave found')
        if not response_reg:
            raise Exception('error: no Ch1_reg wave found')
        if not stimulus:
            raise Exception('couldn\'t find timewave wave in experiment')
        return response, response_reg, stimulus
    else:
        print('\nno .pxp file at path {path}\n')

def pxp_info(response,stimulus, return_data=False):
    print()
    # msPerLine = samples / number of lines / number of frames
    msPerLine = stimulus.size/response.shape[1]/response.shape[0]
    msPerFrame = msPerLine * response.shape[1]
    print(f'msPerLine = {msPerLine}')
    print(f'msPerFrame = {msPerFrame}')
    # to seconds
    linesPerSec = msPerLine/1000
    framesPerSec = msPerFrame/1000
    print('in seconds:')
    print(f'linesPerSec = {linesPerSec}')
    print(f'framesPerSec = {framesPerSec}')
    print(f' => sampling rate = {framesPerSec} Hz')

    # sanity check: get response freq => sample_freq = msPerFrame
    sample_freq = stimulus.shape[0]/response.shape[0]
    print(f'stimulus points = {stimulus.size}')
    # experiment duration (in seconds)
    exp_duration = stimulus.size/1000
    print(f' => experiment duration: {exp_duration} [s]')
    # sampling frequency
    print(f'response datapoints = {response.shape[0]}')
    print(f' => 1 sample every {sample_freq} [ms]')
    
    # check pixel dimensions
    print()
    fov = 610
    nframes, rows, cols = response.shape
    print(f'field of vision (FOV): {fov} (Do check this!)')
    print(f'rows = {rows}, cols = {cols}')
    pixel_dx = fov/cols
    pixel_dy = fov/rows
    pixel_dt = exp_duration/nframes
    print(f'pixel width = {pixel_dx} [µm]')
    print(f'pixel heigh = {pixel_dy} [µm]')
    print(f'pixel dt = {pixel_dt} [s]')
    if cols > rows:
        print(f'so information density is {cols/rows} higher in X than in Y')
    # for transformations
    print('for scalar field transformations: I(x_i, y_j, t_k)')
    print(f'x_i = i * {pixel_dx}')
    print(f'y_j = j * {pixel_dy}')
    print(f't_k = k * {pixel_dt}')
    print()
    
    if return_data:
        # match stimulus to every response sampling point
        stimulus_rx = stimulus[::int(sample_freq)]
        # eventually for transformations
        ijk = np.array([pixel_dx, pixel_dy, pixel_dt])
        return stimulus_rx , ijk


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
            file_ext = string_as_list(file_ext)
        entries = []
        for fe in file_ext:
            entries += [i for i in os.listdir() if i.endswith(file_ext)]
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
                    os.chdir(os.path.join(fname))
                else:
                    return fname
                
                





#
