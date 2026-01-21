# -*- coding: utf-8 -*-

import bokeh.plotting as pbl
import cv2
import datetime
import glob
import holoviews as hv
import logging
import numpy as np
import matplotlib.pyplot as plt
import os
import pandas as pd
import psutil
from pathlib import Path

try:
    cv2.setNumThreads(0)
except:
    pass

import caiman as cm
from caiman.motion_correction import MotionCorrect
from caiman.source_extraction.cnmf import cnmf, params
from caiman.utils.utils import download_demo
from caiman.utils.visualization import plot_contours, nb_view_patches, nb_plot_contour
from caiman.utils.visualization import nb_view_quilt


# set up logging
# Replace with a path if you want to log to a file
logfile = None 
logger = logging.getLogger('caiman')
# Set to logging.INFO if you want much output, potentially much more output
logger.setLevel(logging.WARNING)
logfmt = logging.Formatter('%(relativeCreated)12d [%(filename)s:%(funcName)20s():%(lineno)s] [%(process)d] %(message)s')
if logfile is not None:
    handler = logging.FileHandler(logfile)
else:
    handler = logging.StreamHandler()
handler.setFormatter(logfmt)
logger.addHandler(handler)

# set env variables 
os.environ["MKL_NUM_THREADS"] = "1"
os.environ["OPENBLAS_NUM_THREADS"] = "1"
os.environ["VECLIB_MAXIMUM_THREADS"] = "1"

play_movies = True
movie_path = "C:\\Users\\Fernando\\caiman_data\\example_movies\\Sue_2x_3000_40_-46.tif"
movie = cm.load(movie_path)
print(f'movie path: {movie_path}')
# the play fx has several parameters, like gain, fr (frame rate), do_loop, etc
# movie.play()

# you can concatenate movies by: 
movie_path1 = "C:\\Users\\Fernando\\caiman_data\\example_movies\\Sue_2x_3000_40_-46.tif"
movie_path2 = "C:\\Users\\Fernando\\caiman_data\\example_movies\\Sue_2x_3000_40_-46.tif"
movie_paths = [movie_path1, movie_path2]
movie_orig = cm.load_movie_chain(movie_paths)

# and play movies by:
downsampling_ratio = 0.2  # subsample 5x
movie_orig = movie_orig.resize(fz=downsampling_ratio)
if play_movies:
    movie_orig.play(gain=1.3,
        q_max=99.5, 
        fr=30,
        plot_text=True,
        magnification=2,
        do_loop=False,
        backend='opencv')


# maximum projection (max value of each pixel) # numpy
max_proj_orig = np.max(movie_orig, axis=0)
# correlation image (correlation between pixel and neighborhood)
correlation_image_orig = cm.local_correlations(movie_orig, swap_dim=False)
# get rid of NaNs, in case there are # numpy
correlation_image_orig[np.isnan(correlation_image_orig)] = 0 

# plotting fx - 1 x 2
def plot_proj_corr(max_projection,correlation_image):
    f, (ax_max, ax_corr) = plt.subplots(1,2,figsize=(6,3))
    ax_max.imshow(max_projection, 
                  cmap='viridis',
                  vmin=np.percentile(np.ravel(max_projection),50), 
                  vmax=np.percentile(np.ravel(max_projection),99.5));
    ax_max.set_title("Max Projection Orig", fontsize=12);
    
    ax_corr.imshow(correlation_image_orig, 
                   cmap='viridis', 
                   vmin=np.percentile(np.ravel(correlation_image_orig),50), 
                   vmax=np.percentile(np.ravel(correlation_image_orig),99.5));
    ax_corr.set_title('Correlation Image Orig', fontsize=12);
    plt.show()
    
    

############### set initial parameters
# frame rate (frames per second)
fr = 30
# legth of typical transient 
decay_time = 0.4 
# spatial resolution in x and y (um per pixel)
dxy = (2., 2.)

# motion correction parameters
# new patch for pw-rigid motion correction every x pixels 
strides = (48,48)
# overlap between patches (width of patch = strides + overlaps)
overlaps = (24,24)
# maximum allowed rigid shifts (in pixels)
max_shifts = (6,6)
# maximum shift deviation allowed for patch with respect to rigid shifts
max_deviation_rigid = (3,3)
# flag for performing non-rigid motion correction 
pw_rigid = True

# CNMF parameters for source extraction and deconvolution 
# order of autoregressive system (set p=2 if visible rise time in data)
p = 1
# number of global background components
gnb = 2
# merging threshold, max correlation allowed
merge_thr = 0.85
# enforce nonnegativity constraint on calcium traces (technically on baseline)
bas_nonneg = True
# half-size of the patches in pixels (patch width is rf*2 + 1)
rf = 15
# amount of overlap between the patches in pixels (overlap is stride_cnmf+1)
stride_cnmf = 10
# number of components per patch
K = 4
# expected half-width of neurons in pixels (Gaussian kernel standard deviation)
gSig = np.array([4, 4])
# Gaussian kernel width and hight
gSiz = 2*gSig + 1
# initialization method (if analyzing dendritic data see demo_dendritic.ipynb)
method_init = 'greedy_roi'
# spatial & temporal subsampling during initialization 
ssub = 1
tsub = 1

# parameters for component evaluation
# signal to noise ratio for accepting a component
min_SNR = 2.0
# space correlation threshold for accepting a component
rval_thr = 0.85
# threshold for CNN based classifier
cnn_thr = 0.99
# neurons with cnn probability lower than this value are rejected
cnn_lowest = 0.1

parameter_dict = {'fnames': movie_path,
                  'fr': fr,
                  'dxy': dxy,
                  'decay_time': decay_time,
                  'strides': strides,
                  'overlaps': overlaps,
                  'max_shifts': max_shifts,
                  'max_deviation_rigid': max_deviation_rigid,
                  'pw_rigid': pw_rigid,
                  'p': p,
                  'nb': gnb,
                  'rf': rf,
                  'K': K, 
                  'gSig': gSig,
                  'gSiz': gSiz,
                  'stride': stride_cnmf,
                  'method_init': method_init,
                  'rolling_sum': True,
                  'only_init': True,
                  'ssub': ssub,
                  'tsub': tsub,
                  'merge_thr': merge_thr, 
                  'bas_nonneg': bas_nonneg,
                  'min_SNR': min_SNR,
                  'rval_thr': rval_thr,
                  'use_cnn': True,
                  'min_cnn_thr': cnn_thr,
                  'cnn_lowest': cnn_lowest}

# CNMFParams is the parameters class
parameters = params.CNMFParams(params_dict=parameter_dict)

# it's a dictionary so you can inspect stuff with:
print(parameters.data)
for i in ['fr', 'dxy', 'decay_time']:
    print(parameters.data[i])




########## processing & performance 


print(f"You have {psutil.cpu_count()} CPUs available in your current environment")
# # if set to None, it will use one-less the available number of cpus
num_processors_to_use = None



































#




