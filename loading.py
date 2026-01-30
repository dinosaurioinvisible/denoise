

import os
import time
import numpy as np
from igor2 import packed
import platform
from collections import defaultdict
import tifffile as tf
import stack2stimulus


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


def load_reg_stim(path):
    # try to load from files in folder
    # if path = full path
    fpath = None
    if os.path.isfile(str(path)) and (path.endswith('.tif') or path.endswith('.tiff')):
        fpath = path
    # if path = dir, look for tif/tiff files inside
    elif os.path.isdir(str(path)):
        # look for reg file
        for filename in os.listdir(str(path)):
            if filename.endswith('.tif') or filename.endswith('tiff'):
                if 'reg' in filename.split('_'):
                    fpath = filename
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
    # else, fpath is correct, but couldn't open file (prob .pxp)
    # else:

    # TODO: same code as above - make fx
    # if igor exp
    import pdb; pdb.set_trace()
    if os.path.isfile(str(path)) and ends.endswith('.pxp'):
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
            fpath = None
    elif fpath:
        # if tif file: try to load tiff & itx files from folder
        response, response_reg, stimulus = None, None, None
        # opt1: (response_reg + .itx file)
        # opt2: response (raw): ch1 => response_reg, ch2 => stimulus (if needed)
        print('\ntryng to load individual files from folder')
        print(f'stack: {fpath}')
        # look for reg file and raw stacks
        import pdb; pdb.set_trace()
        try:
            if 'reg' in fpath.split('_'):
                response_reg = tf.imread(fpath)
                print(f'loaded registered stack at {fpath}')
            else:
                response = tf.imread(fpath)
                print(f'loaded raw stack at {fpath}')
        except:
            print(f'couldn\'t load stack at {fpath}')
            fpath = None
        # now depending on which files there are:
        # 1) response reg + itx
        # 2) response reg + response -> itx
        if response_reg:
            fpath_itx = search_in_filedir(fpath,'itx')
            if fpath_itx:
                print(f'loading .itx file for stimulus: {fpath_itx}')
                try:
                    stimulus = read_itx(fpath_itx)
                    print(f'ok')
                except:
                    print(f'\ncouldn\'t load .itf file at {fpath_itx}\n')
            else:
                # look for raw file
                tifs = search_in_filedir(fpath,ext='tif,tiff')

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



x = '/Users/f/Dropbox/_r66y/r66xe/2p_data/ca_a1'
load_reg_stim(x)






# load or register with caiman
# fname_caiman = [x for x in os.listdir(exp_path) if x.endswith('caimanreg.tif')][0]
# fpath_caiman = f'{exp_path}{sep}{fname_caiman}'
# fpath_caiman = ''
# if not os.path.isfile(fpath_caiman):
#     max_shifts = (6, 6)  # maximum allowed rigid shift in pixels (view the movie to get a sense of motion)
#     # strides =  (48, 48)  # create a new patch every x pixels for pw-rigid correction
#     # overlaps = (24, 24)  # overlap between patches (size of patch strides+overlaps) / pw
#     max_deviation_rigid = 3   # maximum deviation allowed for patch with respect to rigid shifts
#     pw_rigid = False # flag for performing rigid or piecewise rigid motion correction
#     shifts_opencv = True  # flag for correcting motion using bicubic interpolation (otherwise FFT interpolation is used)
#     border_nan = 'copy'  # replicate values along the boundary (if True, fill in with NaN)
#     # create a motion correction object
#     tif_fpath = f'{exp_path}{sep}{fname}_de-int.tif'
#     if not os.path.isfile(tif_fpath):
#         print(f'\ncouldn\'t find {tif_fpath}')
#         tif_fpath = file_menu(exp_path, file_ext='tif')
#     mc = MotionCorrect(tif_fpath, dview=None, max_shifts=max_shifts,
#                       # strides=strides, overlaps=overlaps,
#                       max_deviation_rigid=max_deviation_rigid,
#                       shifts_opencv=shifts_opencv, nonneg_movie=True,
#                       border_nan=border_nan)

#     mc.motion_correct(save_movie=True)
#     m_rig = cm.load(mc.mmap_file)
#     # save
#     tf.imwrite(f'{fpath_caiman}', m_rig)
#     print(f'\nsaved at : {fpath_caiman} \n')
# # load caiman reg file
# response_caimanreg = tf.imread(fpath_caiman)















#
