# -*- coding: utf-8 -*-

import cv2
import matplotlib.pyplot as plt
import numpy as np
import os
# import logging
import caiman as cm
from caiman.motion_correction import MotionCorrect, tile_and_correct, motion_correction_piecewise

try:
    cv2.setNumThreads(0)
except Exception:
    pass

# for multiprocessing
# dview = None
# if 'dview' in locals():
#     cm.stop_server(dview=dview)
# c, dview, n_processes = cm.cluster.setup_cluster(
#     backend='multiprocessing', n_processes=None, single_thread=False)

play_movies = False

fname = 'C:/Users/Fernando/zf/data/ca_a1/step_HUC_a1_de-int.tiff'

max_shifts = (6, 6)  # maximum allowed rigid shift in pixels (view the movie to get a sense of motion)
strides =  (48, 48)  # create a new patch every x pixels for pw-rigid correction
overlaps = (24, 24)  # overlap between patches (size of patch strides+overlaps)
max_deviation_rigid = 3   # maximum deviation allowed for patch with respect to rigid shifts
pw_rigid = True    # flag for performing rigid or piecewise rigid motion correction
shifts_opencv = True  # flag for correcting motion using bicubic interpolation (otherwise FFT interpolation is used)
border_nan = 'copy'  # replicate values along the boundary (if True, fill in with NaN)

# create a motion correction object
mc = MotionCorrect(fname, dview=None, max_shifts=max_shifts,
                  strides=strides, overlaps=overlaps,
                  max_deviation_rigid=max_deviation_rigid,
                  shifts_opencv=shifts_opencv, nonneg_movie=True,
                  border_nan=border_nan)

mc.motion_correct(save_movie=True)

# load motion corrected movie
m_rig = cm.load(mc.mmap_file)
bord_px_rig = np.ceil(np.max(mc.shifts_rig)).astype(int)

#%% visualize templates
plt.figure(figsize = (20,10))
plt.imshow(mc.total_template_rig, cmap = 'gray');

# inspect movie
downsample_ratio = 0.2
m_rig.resize(1, 1, downsample_ratio)
if play_movies:
    m_rig.play(
         q_max=99.5, fr=30, magnification=2, bord_px = 0*bord_px_rig) # press q to exit

import tifffile as tf
fname = fname.split('/')[-1].split('.')[0]
tf.imwrite(f'{fname}_caimanreg.tif', m_rig)
print(f'saved as : {fname}')


















#
