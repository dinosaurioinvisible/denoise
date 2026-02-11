# -*- coding: utf-8 -*-

from platform import system
from loading import load_pxp, pxp_info
from stack2stimulus import mk_step_indexes
import numpy as np
import matplotlib.pyplot as plt

# simple script to automatically look for synapses using KS method


# load: raw, registered & stimulus
if system() == 'Windows':
    response, response_reg, stimulus = load_pxp('C:\\Users\\Fernando\\zf\\data\\jose_data\\Glutamate_Tectum\\F1_glut_HUC_AF10\\a1\\steps_pre_AF10_a1001.pxp')
    # response, response_reg, stimulus = load_pxp('C:\\Users\\Fernando\\zf\\data\\jose_data\\Glutamate_Tectum\\F1_glut_HUC_AF10\\a2\\Steps_pre_AF10_a2008.pxp')
    # response, response_reg, stimulus = load_pxp('C:\\Users\\Fernando\\zf\\data\\jose_data\\Glutamate_Tectum\\F2_glut_HUC_AF10\\A1\\Steps_pre_AF10_a1015.pxp')
    # response, response_reg, stimulus = load_pxp('C:\\Users\\Fernando\\zf\\data\\jose_data\\Glutamate_Tectum\\F2_glut_HUC_AF10\\A2\\steps_pre_AF10_a2021.pxp')
    # response, response_reg, stimulus = load_pxp('C:\\Users\\Fernando\\zf\\data\\jose_data\\Glutamate_Tectum\\F3_glut_HUC_AF10\\a1\\steps_pre_AF10_a1034.pxp')
    # response, response_reg, stimulus = load_pxp('C:\\Users\\Fernando\\zf\\data\\jose_data\\Glutamate_Tectum\\F3_glut_HUC_AF10\\a2\\steps_pre_AF10_a1038.pxp')
    # response, response_reg, stimulus = load_pxp('C:\\Users\\Fernando\\zf\\data\\jose_data\\Glutamate_Tectum\\F4_glut_HUC_AF10\\A1\\step_AF10_a1001.pxp')
    # response, response_reg, stimulus = load_pxp('C:\\Users\\Fernando\\zf\\data\\jose_data\\Glutamate_Tectum\\F4_glut_HUC_AF10\\A2\\step_AF10_a2006.pxp')
    # response, response_reg, stimulus = load_pxp('C:\\Users\\Fernando\\zf\\data\\jose_data\\Glutamate_Tectum\\F5_glut_HUC_AF10\\A1\\STEP_AF10_a1012.pxp')
    # response, response_reg, stimulus = load_pxp('C:\\Users\\Fernando\\zf\\data\\jose_data\\Glutamate_Tectum\\F5_glut_HUC_AF10\\A2\\STEP_AF10_a2017.pxp')
    # response, response_reg, stimulus = load_pxp('C:\\Users\\Fernando\\zf\\data\\jose_data\\Glutamate_Tectum\\F6_glut_HUC_AF10\\a1\\steps_pre_AF10_a1029.pxp')
    # response, response_reg, stimulus = load_pxp('C:\\Users\\Fernando\\zf\\data\\jose_data\\Glutamate_Tectum\\F6_glut_HUC_AF10\\a2\\steps_pre_AF10_a1034.pxp')
    # response, response_reg, stimulus = load_pxp('C:\\Users\\Fernando\\zf\\data\\jose_data\\Glutamate_Tectum\\F7_glut_HUC_AF10\\steps_pre_AF10_a1039.pxp')
    # response = tf.imread('C:\\Users\\Fernando\\zf\\data\\glu_a1\\steps_pre_AF10_a1001.tif')
    # response_reg = tf.imread('C:\\Users\\Fernando\\zf\\data\\glu_a1\\steps_pre_AF10_a1001_Ch1_reg.tif')
    # stimulus = read_itx('C:\\Users\\Fernando\\zf\\data\\glu_a1\\steps_timewave.itx')
else:
    fpath = '/Users/f/Dropbox/_r66y/r66xe/2p_data/jose_glu_exps/steps_pre_af10_a1001.pxp'
    # fpath = '/Users/f/Dropbox/_r66y/r66xe/2p_data/jose_glu_exps/Steps_pre_AF10_a2008.pxp'
    # fpath = '/Users/f/Dropbox/_r66y/r66xe/2p_data/jose_glu_exps/Steps_pre_AF10_a1015.pxp'
    response, response_reg, stimulus = load_pxp(fpath)

# check units, dimensions & print some data
# returns stim points matching response + scalar field coeffs for eventual transformations 
stimulus, ijk = pxp_info(response, stimulus, return_data=True)

# split into activity & baseline
steps, ixs_baseline, ixs_activity = mk_step_indexes(stimulus, split_by='activity')

# mk pixel wise distributions 


# mk map of difference between distributions using ks-method

# mk 2D gaussian filter (consider real sizes 2m x 2m)

# apply filter get maxima & sort 

# apply 2D filter to every slice in the stack & get temp local maxima

