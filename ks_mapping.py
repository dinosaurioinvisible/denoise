# -*- coding: utf-8 -*-

from platform import system
from loading import load_pxp, pxp_info
from stack2stimulus import mk_step_indexes
import numpy as np
from scipy.stats import kstest
from scipy.stats import wasserstein_distance as emd
from skimage.feature import peak_local_max
import matplotlib.pyplot as plt
from tqdm import tqdm
import seaborn as sns
import cv2
from scipy.ndimage import gaussian_filter1d

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

# simple check
plt.imshow(response.mean(axis=0))
plt.show()

# split into activity & baseline
steps, ixs_baseline, ixs_activity = mk_step_indexes(stimulus, split_by='activity')

# mk pixel-wise map of difference between distributions using ks-method
def pixel_wise_comparison(arr1,arr2):
    if arr1.shape[1:] != arr2.shape[1:]:
        raise Exception('comparing apples with pears? (arrays have different dimensions)')
    nframes,rows,cols = arr1.shape
    vmap = np.zeros((rows, cols))
    wmap = np.zeros((rows, cols))
    for row in tqdm(range(rows)):
        for col in range(cols):
            x = kstest(arr1[:,row,col], arr2[:,row,col])
            vmap[row,col] = x.statistic
            wmap[row,col] = emd(arr1[:,row,col], arr2[:,row,col])
    return vmap, wmap

baseline = response[ixs_baseline]
rx = response[ixs_activity]
ks_map, emd_map = pixel_wise_comparison(baseline,rx)

plt.imshow(ks_map)
plt.show()

plt.imshow(emd_map)
plt.show()


# TODO: overley in red
# look for maxima
def get_maxima(arr, min_distance=1, num_peaks=50):
    maxima = peak_local_max(arr, min_distance=min_distance, num_peaks=num_peaks)
    mask = np.zeros((arr.shape))
    for mr,mc in maxima:
        mask[mr,mc] = arr[mr,mc]
    plt.imshow(response.mean(axis=0), alpha=0.9)
    plt.imshow(mask, alpha=0.7)
    plt.title(f'maxima points = {num_peaks}')
    plt.show()
    return maxima, mask

ks_map_maxima, ks_map_mask = get_maxima(ks_map, num_peaks=33)
emd_map_maxima, emd_map_mask = get_maxima(emd_map, num_peaks=33)

# look individual points distributions
def compare_pixel_dists(arr1,arr2,row,col, arr3=[], label1='arr1', label2='arr2', label3='arr3'):
    sns.distplot(arr1[:,row,col], label=label1)
    sns.distplot(arr2[:,row,col], label=label2)
    if arr3:
        sns.distplot(arr3[:,row,col], label=label3)
    plt.legend()
    plt.title(f'row = {row}, col = {col}')
    plt.show()
    # plt.plot(arr1[:,row,col], label=label1, alpha=0.9)
    # plt.plot(arr2[:,row,col], label=label2, alpha=0.5)
    # plt.legend()
    # plt.title(f'row = {row}, col = {col}')
    # plt.show()

def compare_pixel_dists_many(arr1,arr2,pxs, arr3=[],arr4=[], label1='arr1', label2='arr2', label3='label3'):
    for row,col in pxs:
        compare_pixel_dists(arr1,arr2,row,col, arr3=arr3,label1=label1,label2=label2,label3=label3)

# compare_pixel_dists_many(baseline,rx,ks_map_maxima,label1='baseline',label2='response')
# plt.imshow(ks_map)
# plt.show()
# compare_pixel_dists_many(baseline,rx,emd_map_maxima,label1='baseline',label2='response')
# plt.imshow(emd_map)
# plt.show()


# apply 2D filter to every slice in the stack & get temp local maxima








































#