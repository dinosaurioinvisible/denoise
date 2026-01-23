
import os
from auxs import *
import tifffile as tf
import numpy as np
import matplotlib.pyplot as plt
import platform

# get stack/movie
if platform.system() == "Darwin":
    fpath = "/Users/f/Dropbox/_r66y/r66xe/2p_data/step_a1.tif"
elif platform.system() == "Windows":
    fpath = 'C:/Users/Fernando/zf/data/ca_a1/step_HUC_a1.tif'

# if not, look for file in parent folders
if not os.path.isfile(fpath):
    exp_name = fpath.split('/')[-1]
    fpath = dir_upsearch(dirname='data',filename=exp_name,verbose=True)
# if not, load the menu
if not os.path.isfile(fpath):
    fpath = file_menu(path=fpath, file_ext=['tif','tiff'])

# actually load
stack = tf.imread(fpath)

# de-interleave & register
response, ch2 = deinterleave(stack)

# load itx file for channel 2
# TODO: extract stimuls - for now using itx file made in Igor
fpath_itx = 'C:/Users/Fernando/zf/data/ca_a1/steps_timewave.itx'
# if not, load the menu
if not os.path.isfile(fpath):
    fpath_itx = file_menu(path=fpath, file_ext='itx')
itx_points = read_itx(fpath_itx)

print(f'itx points: {len(itx_points)}')

# get steps
steps_vals = get_steps_vals(itx_points)

# get response freq
rx_freq = len(itx_points)/response.shape[0]

# TODO: get metadata from tiff file










































#
