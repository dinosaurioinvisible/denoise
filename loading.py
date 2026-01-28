

import os
import time
import numpy as np
from igor2 import packed
import platform
from collections import defaultdict
import tifffile as tf
import stack2stimulus


# wrapper for loading imaging data
def load_reg_stim(path):
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
        # look for reg file and raw stacks
        try:
            if 'reg' in fpath.split('_'):
                response_reg = tf.imread(fpath)
                print(f'loaded registered stack at {fpath}')
            else:
                response = tf.imread(fpath)
                print(f'loaded raw stack at {fpath}')
        except:
            print(f'\ncouldn\'t load stack at {fpath}\n')
            fpath = None
        # now depending on which files there are:
        # 1) response reg + itx
        # 2) response reg + response -> itx
        if response_reg:
            fpath_itx = search_ext_in_filedir(fpath,'itx')
            if fpath_itx:
                print(f'loading .itx file for stimulus: {fpath_itx}')
                try:
                    stimulus = read_itx(fpath_itx)
                    print(f'ok')
                except:
                    print(f'\ncouldn\'t load .itf file at {fpath_itx}\n')
            else:
                # look for raw file




        if (fpath and response) or (fpath and response_reg):
            # load itx file with stimulus data, assuming same folder
            sep = '\\' if platform.system() == 'Windows' else '/'
            exp_path = sep.join(fpath.split(sep)[:-1])
            itxs = [x for x in os.listdir(exp_path) if x.endswith('.itx')]
            fname_itx = itxs[0] if len(itxs) > 0 else None
            if fname_itx:
                fpath_itx = os.path.join(exp_path,fname_itx)

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

























#
