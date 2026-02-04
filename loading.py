

import os
import time
import numpy as np
from igor2 import packed
import platform
from collections import defaultdict
import tifffile as tf
import stack2stimulus
# from auxs import print_wave_data


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








#
