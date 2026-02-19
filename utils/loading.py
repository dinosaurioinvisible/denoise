

import os
# import time
import numpy as np
from igor2 import packed
import platform
from utils.auxs import string_as_list


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
        fpath = file_menu(file_ext='tif, tiff, pxp')
        return
    # 2) try to load igor exp
    if fpath:
        print(f'\ntrying to load .pxp file at {fpath}')
        rx_wave, reg_wave, sti_wave, console_info = load_waves_from_igor_exp(fpath)
        # transpose axes: [time][y][x] => [t][row][col]
        response = rx_wave['wData'].T
        response_reg = reg_wave['wData'].T
        stimulus = sti_wave['wData']
        stimulus = stimulus/10**6 if stimulus.mean() > 100 else stimulus
        info = {}
        console_info = console_info.split('\n')[1:5]
        for ci in console_info:
            k,v = ci.split(' was ')
            k = k.lstrip().rstrip()
            info[k] = v
        return response, response_reg, stimulus, info


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
        for record in pxp[0]:
            # recordType = 2: info from console
            # recordType = 4: info from ART config
            if record.header['recordType'] == 2:
                info = record.text.decode()
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
                # if k.endswith('_a1001'):
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
        return response, response_reg, stimulus, info
    else:
        print('\nno .pxp file at path {path}\n')

def pxp_info(response,stimulus, igor_info=None,return_data=False):
    print()
    data = {}
    # msPerLine = samples / number of lines / number of frames
    msPerLine = stimulus.size/response.shape[1]/response.shape[0]
    msPerFrame = msPerLine * response.shape[1]
    linesPerSec = msPerLine/1000
    framesPerSec = msPerFrame/1000
    data['msPerLine'] = msPerLine
    data['msPerFrame'] = msPerFrame
    data['linesPerSec'] = linesPerSec
    data['framesPerSec'] = framesPerSec
    print(f'msPerLine = {msPerLine}')
    print(f'linesPerSec = {linesPerSec}')
    print(f'msPerFrame = {msPerFrame}')    
    print(f'framesPerSec = {framesPerSec}')
    freq = 1/framesPerSec
    data['frequency'] = freq
    print(f' => sampling rate (frequency) = {freq} [Hz]')

    # sanity check: get response freq => sample_freq = msPerFrame
    stimulusDataPoints = stimulus.size
    data['stimulusDataPoints'] = stimulusDataPoints
    print(f'\nstimulus points = {stimulusDataPoints}')
    # experiment duration (in seconds)
    exp_duration = stimulus.size/1000
    data['experimentDuration'] = exp_duration
    print(f' => experiment duration: {exp_duration} [s]')
    # sampling frequency
    responseDataPoints = response.shape[0]
    data['responseDataPoints'] = responseDataPoints
    samplingRate = stimulusDataPoints/responseDataPoints
    # same as frequency, but just to 2ble check
    data['samplingRate'] = samplingRate
    print(f'response datapoints = {response.shape[0]}')
    print(f' => 1 sample every {samplingRate} [ms]')
    
    # check pixel dimensions
    print()
    fov = 610
    nframes, rows, cols = response.shape
    data['fov'] = fov
    data['nframes'] = nframes
    data['rows'] = rows
    data['cols'] = cols
    print(f'field of vision (FOV): {fov} (Do check this!)')
    print(f'rows = {rows}, cols = {cols}')
    pixel_dx = fov/cols
    pixel_dy = fov/rows
    pixel_dt = exp_duration/nframes
    print(f'pixel width at zoom 1.0 = {pixel_dx} [µm]')
    print(f'pixel heigh at zoom 1.0 = {pixel_dy} [µm]')
    print(f'pixel dt = {pixel_dt} [s]')
    if cols > rows:
        print(f'so information density is {cols/rows} higher in X than in Y')
    # for transformations
    # print('for scalar field transformations: I(x_i, y_j, t_k)')
    # print(f'x_i = i * {pixel_dx}')
    # print(f'y_j = j * {pixel_dy}')
    # print(f't_k = k * {pixel_dt}')
    # print()
    
    # info from igor console
    if isinstance(igor_info, dict):
        print('\nIgor info:')
        for k,v in igor_info.items():
            print(f' {k}: {v}')
        zoom = float(igor_info['zoom'])
        frame_dim = fov/zoom
        data['zoom'] = zoom
        data['frameSide'] = frame_dim
        print(f'frame side physical size = {frame_dim:.2f} [µm]')
        pixel_dx /= zoom
        pixel_dy /= zoom
        data['pixel_dx'] = pixel_dx
        data['pixel_dy'] = pixel_dy
        data['pixel_dt'] = pixel_dt
        print(f'pixel physical height & width = {pixel_dy:.2f} x {pixel_dx:.2f} µm')
        # synapse_dx, synapse_dy = 2.5, 2.5     # retina
        synapse_dx, synapse_dy = 1.5, 1.5       # tectum
        data['synapse_dx'] = synapse_dx
        data['synapse_dy'] = synapse_dy
        print(f'synaptic button approx. area: {synapse_dx} x {synapse_dy} µms')
        dxpx = synapse_dx/pixel_dx
        dypy = synapse_dy/pixel_dy
        data['ncolsPerSynapse'] = dypy
        data['nrowsPerSynapse'] = dxpx
        print(' => approx. pixel patch needed for a synapse:')
        sxpx = pixel_dx/synapse_dx
        sypy = pixel_dy/synapse_dy
        data['nSynapsesPerCol'] = sypy
        data['nSynapsesPerRow'] = sxpx
        print(f'cols per synapse: {dypy:.2f} <-> {sypy:.2f} synapses per cols')
        print(f'rows per synapse: {dxpx:.2f} <-> {sxpx:.2f} synapses per rows')
        print()


    if return_data:
        # match stimulus to every response sampling point
        stimulus_rx = stimulus[::int(samplingRate)]
        # eventually for transformations
        # ijk = np.array([pixel_dx, pixel_dy, pixel_dt])
        return stimulus_rx, data


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
