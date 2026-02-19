#!/usr/bin/env python3
# -*- coding: utf-8 -*-


from platform import system
from utils.loading import load_pxp, pxp_info
from utils.stack2stimulus import mk_step_indexes
import numpy as np
from scipy.stats import kstest
from scipy.stats import wasserstein_distance as emd
from skimage.feature import peak_local_max
import matplotlib.pyplot as plt
from utils.plotting_fxs import mk_plots, overlaying_imshows, simple_plot
from utils.auxs import tile2arr2, datapoints_in_seconds
from utils.improc import gauss1d, conv3d
from tqdm import tqdm
import seaborn as sns


# direct loading for now
if system() == 'Windows':
    fpath = 'C:\\Users\\Fernando\\zf\\data\\jose_data\\Glutamate_Tectum\\F1_glut_HUC_AF10\\a1\\steps_pre_AF10_a1001.pxp'
    # fpath = 'C:\\Users\\Fernando\\zf\\data\\jose_data\\Glutamate_Tectum\\F1_glut_HUC_AF10\\a2\\Steps_pre_AF10_a2008.pxp'
    # fpath = 'C:\\Users\\Fernando\\zf\\data\\jose_data\\Glutamate_Tectum\\F2_glut_HUC_AF10\\A1\\Steps_pre_AF10_a1015.pxp'
    # fpath = 'C:\\Users\\Fernando\\zf\\data\\jose_data\\Glutamate_Tectum\\F2_glut_HUC_AF10\\A2\\steps_pre_AF10_a2021.pxp'
    # fpath = 'C:\\Users\\Fernando\\zf\\data\\jose_data\\Glutamate_Tectum\\F3_glut_HUC_AF10\\a1\\steps_pre_AF10_a1034.pxp'
    # fpath = 'C:\\Users\\Fernando\\zf\\data\\jose_data\\Glutamate_Tectum\\F3_glut_HUC_AF10\\a2\\steps_pre_AF10_a1038.pxp'
    # fpath = 'C:\\Users\\Fernando\\zf\\data\\jose_data\\Glutamate_Tectum\\F4_glut_HUC_AF10\\A1\\step_AF10_a1001.pxp'
    # fpath = 'C:\\Users\\Fernando\\zf\\data\\jose_data\\Glutamate_Tectum\\F4_glut_HUC_AF10\\A2\\step_AF10_a2006.pxp'
    # fpath = 'C:\\Users\\Fernando\\zf\\data\\jose_data\\Glutamate_Tectum\\F5_glut_HUC_AF10\\A1\\STEP_AF10_a1012.pxp'
    # fpath = 'C:\\Users\\Fernando\\zf\\data\\jose_data\\Glutamate_Tectum\\F5_glut_HUC_AF10\\A2\\STEP_AF10_a2017.pxp'
    # fpath = 'C:\\Users\\Fernando\\zf\\data\\jose_data\\Glutamate_Tectum\\F6_glut_HUC_AF10\\a1\\steps_pre_AF10_a1029.pxp'
    # fpath = 'C:\\Users\\Fernando\\zf\\data\\jose_data\\Glutamate_Tectum\\F6_glut_HUC_AF10\\a2\\steps_pre_AF10_a1034.pxp'
    # fpath = 'C:\\Users\\Fernando\\zf\\data\\jose_data\\Glutamate_Tectum\\F7_glut_HUC_AF10\\steps_pre_AF10_a1039.pxp'
    # response = tf.imread('C:\\Users\\Fernando\\zf\\data\\glu_a1\\steps_pre_AF10_a1001.tif')
    # response_reg = tf.imread('C:\\Users\\Fernando\\zf\\data\\glu_a1\\steps_pre_AF10_a1001_Ch1_reg.tif')
    # stimulus = read_itx('C:\\Users\\Fernando\\zf\\data\\glu_a1\\steps_timewave.itx')
    response, response_reg, stimulus, igor_info = load_pxp(fpath)
else:
    fpath = '/Users/f/Dropbox/_r66y/r66xe/2p_data/jose_glu_exps/steps_AF10_a1001.pxp'
    # fpath = '/Users/f/Dropbox/_r66y/r66xe/2p_data/jose_glu_exps/steps_AF10_a1012.pxp'
    # fpath = '/Users/f/Dropbox/_r66y/r66xe/2p_data/jose_glu_exps/steps_AF10_a2017.pxp'
    # fpath = '/Users/f/Dropbox/_r66y/r66xe/2p_data/jose_glu_exps/steps_AF10_a2006.pxp'
    # fpath = '/Users/f/Dropbox/_r66y/r66xe/2p_data/jose_glu_exps/steps_pre_AF10_a1001.pxp'
    # fpath = '/Users/f/Dropbox/_r66y/r66xe/2p_data/jose_glu_exps/Steps_pre_AF10_a1015.pxp'
    # fpath = '/Users/f/Dropbox/_r66y/r66xe/2p_data/jose_glu_exps/steps_pre_AF10_a1029.pxp'
    # fpath = '/Users/f/Dropbox/_r66y/r66xe/2p_data/jose_glu_exps/steps_pre_AF10_a1034.pxp'
    # fpath = '/Users/f/Dropbox/_r66y/r66xe/2p_data/jose_glu_exps/steps_pre_AF10_a1038.pxp'
    # fpath = '/Users/f/Dropbox/_r66y/r66xe/2p_data/jose_glu_exps/steps_pre_AF10_a1039.pxp'
    # fpath = '/Users/f/Dropbox/_r66y/r66xe/2p_data/jose_glu_exps/steps_pre_AF10_a2008.pxp'
    # fpath = '/Users/f/Dropbox/_r66y/r66xe/2p_data/jose_glu_exps/steps_pre_AF10_a2021.pxp'
    response, response_reg, stimulus, igor_info = load_pxp(fpath)


# check units, dimensions & print some data
stimulus, data = pxp_info(response, stimulus, igor_info, return_data=True)
stimulus_points = datapoints_in_seconds(stimulus, data['frequency'])

# plot some basics
simple_plot(stimulus_points,stimulus)
simple_plot(response.mean(axis=0), title='response average', mk_cbar=True)
simple_plot(response_reg.mean(axis=0), title='registered response average', mk_cbar=True)

# split into activity & baseline
steps, ixs_baseline, ixs_activity = mk_step_indexes(stimulus, split_by='activity')

#####################################################################
                    # image substraction
#####################################################################    

rx_sub = response - response.mean(axis=0)

# make raster plot

# make circles around rois
























































#
