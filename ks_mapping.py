# -*- coding: utf-8 -*-

from platform import system
from utils.loading import load_pxp, pxp_info
from utils.stack2stimulus import mk_step_indexes
import numpy as np
from scipy.stats import kstest
from scipy.stats import wasserstein_distance as emd
from skimage.feature import peak_local_max
import matplotlib.pyplot as plt
from utils.plotting_fxs import mk_plots, overlaying_imshows
from utils.auxs import tile2arr2
from utils.improc import gauss1d, conv3d
from tqdm import tqdm
import seaborn as sns

# simple script to automatically look for synapses using KS method


# load: raw, registered & stimulus
if system() == 'Windows':
    fpath = 'C:\\Users\\Fernando\\zf\\data\\jose_data\\Glutamate_Tectum\\F1_glut_HUC_AF10\\a1\\steps_pre_AF10_a1001.pxp'
    fpath = 'C:\\Users\\Fernando\\zf\\data\\jose_data\\Glutamate_Tectum\\F1_glut_HUC_AF10\\a2\\Steps_pre_AF10_a2008.pxp'
    fpath = 'C:\\Users\\Fernando\\zf\\data\\jose_data\\Glutamate_Tectum\\F2_glut_HUC_AF10\\A1\\Steps_pre_AF10_a1015.pxp'
    fpath = 'C:\\Users\\Fernando\\zf\\data\\jose_data\\Glutamate_Tectum\\F2_glut_HUC_AF10\\A2\\steps_pre_AF10_a2021.pxp'
    fpath = 'C:\\Users\\Fernando\\zf\\data\\jose_data\\Glutamate_Tectum\\F3_glut_HUC_AF10\\a1\\steps_pre_AF10_a1034.pxp'
    fpath = 'C:\\Users\\Fernando\\zf\\data\\jose_data\\Glutamate_Tectum\\F3_glut_HUC_AF10\\a2\\steps_pre_AF10_a1038.pxp'
    fpath = 'C:\\Users\\Fernando\\zf\\data\\jose_data\\Glutamate_Tectum\\F4_glut_HUC_AF10\\A1\\step_AF10_a1001.pxp'
    fpath = 'C:\\Users\\Fernando\\zf\\data\\jose_data\\Glutamate_Tectum\\F4_glut_HUC_AF10\\A2\\step_AF10_a2006.pxp'
    fpath = 'C:\\Users\\Fernando\\zf\\data\\jose_data\\Glutamate_Tectum\\F5_glut_HUC_AF10\\A1\\STEP_AF10_a1012.pxp'
    fpath = 'C:\\Users\\Fernando\\zf\\data\\jose_data\\Glutamate_Tectum\\F5_glut_HUC_AF10\\A2\\STEP_AF10_a2017.pxp'
    fpath = 'C:\\Users\\Fernando\\zf\\data\\jose_data\\Glutamate_Tectum\\F6_glut_HUC_AF10\\a1\\steps_pre_AF10_a1029.pxp'
    fpath = 'C:\\Users\\Fernando\\zf\\data\\jose_data\\Glutamate_Tectum\\F6_glut_HUC_AF10\\a2\\steps_pre_AF10_a1034.pxp'
    fpath = 'C:\\Users\\Fernando\\zf\\data\\jose_data\\Glutamate_Tectum\\F7_glut_HUC_AF10\\steps_pre_AF10_a1039.pxp'
    # response = tf.imread('C:\\Users\\Fernando\\zf\\data\\glu_a1\\steps_pre_AF10_a1001.tif')
    # response_reg = tf.imread('C:\\Users\\Fernando\\zf\\data\\glu_a1\\steps_pre_AF10_a1001_Ch1_reg.tif')
    # stimulus = read_itx('C:\\Users\\Fernando\\zf\\data\\glu_a1\\steps_timewave.itx')
    response, response_reg, stimulus, igor_info = load_pxp(fpath)
else:
    # fpath = '/Users/f/Dropbox/_r66y/r66xe/2p_data/jose_glu_exps/steps_pre_af10_a1001.pxp'
    # fpath = '/Users/f/Dropbox/_r66y/r66xe/2p_data/jose_glu_exps/Steps_pre_AF10_a2008.pxp'
    fpath = '/Users/f/Dropbox/_r66y/r66xe/2p_data/jose_glu_exps/Steps_pre_AF10_a1015.pxp'
    # fpath = '/Users/f/Dropbox/_r66y/r66xe/2p_data/jose_glu_exps/steps_pre_AF10_a2021.pxp'
    # fpath = '/Users/f/Dropbox/_r66y/r66xe/2p_data/jose_glu_exps/steps_pre_AF10_a1034.pxp'
    # fpath = '/Users/f/Dropbox/_r66y/r66xe/2p_data/jose_glu_exps/steps_pre_AF10_a1038.pxp'
    response, response_reg, stimulus, igor_info = load_pxp(fpath)

# check units, dimensions & print some data
# returns stim points matching response + scalar field coeffs for eventual transformations 
stimulus, ijk = pxp_info(response, stimulus, igor_info, return_data=True)

# split into activity & baseline
steps, ixs_baseline, ixs_activity = mk_step_indexes(stimulus, split_by='activity')

# mk pixel-wise map of difference between distributions using ks-method
def pixel_wise_comparison(arr1,arr2):
    print(f'\npixel wise comparison: ks-map & emd-map')
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

# simple check
mk_plots(response.mean(axis=0), title='average')
mk_plots(response_reg.mean(axis=0), title='average reg')

# no reg
baseline = response[ixs_baseline]
rx = response[ixs_activity]
ks_map, emd_map = pixel_wise_comparison(baseline,rx)
# reg
baseline_reg = response_reg[ixs_baseline]
reg = response_reg[ixs_activity]
ks_regmap, emd_regmap = pixel_wise_comparison(baseline_reg,reg)

mk_plots(ks_map, title='ks map')
mk_plots(ks_regmap, title='ks reg map')
mk_plots(emd_map, title='emd map')
mk_plots(emd_regmap, title='emd reg map')


# difference of 2 2d-gaussians - for band pass filtering




# look for maxima
def get_maxima(arr, min_distance=1, num_peaks=50,title=''):
    maxima = peak_local_max(arr, min_distance=min_distance, num_peaks=num_peaks)
    mask = np.zeros((arr.shape))
    for mr,mc in maxima:
        mask[mr,mc] = arr[mr,mc]
    title = f'{title} - maxima={num_peaks}'
    overlaying_imshows(arr, mask, title=title)
    overlaying_imshows(response.mean(axis=0), mask, title=title)
    return maxima, mask

ks_maxima, ks_mask = get_maxima(ks_map, num_peaks=33, title='ks maxima')
ks_maxima_reg, ks_reg_mask = get_maxima(ks_regmap, num_peaks=33, title='ks reg maxima')
emd_maxima, emd_mask = get_maxima(emd_map, num_peaks=33, title='emd maxima')
emd_maxima_reg, emd_reg_mask = get_maxima(emd_regmap, num_peaks=33, title='emd reg maxima')

# TODO: include kurtosis value
# plot individual points distributions: look for kurtosis
def compare_pixel_dists(arr1,arr2,row,col, arr3=[],
                        label1='arr1', label2='arr2', label3='arr3',
                        title='', mk_distplots=False):
    sns.histplot(arr1[:,row,col], label=label1, kde=True)
    sns.histplot(arr2[:,row,col], label=label2, kde=True)
    if arr3:
        sns.histplot(arr3[:,row,col], label=label3, kde=True)
    if mk_distplots:
        plt.legend()
        plt.title(f'{title} - row = {row}, col = {col}')
        plt.show()
        sns.distplot(arr1[:,row,col], label=label1)
        sns.distplot(arr2[:,row,col], label=label2)
        if arr3:
            sns.distplot(arr3[:,row,col], label=label3)
    plt.legend()
    plt.title(f'{title} - row = {row}, col = {col}')
    plt.show()
def compare_pixel_dists_many(arr1,arr2,pxs, arr3=[],arr4=[], label1='arr1', label2='arr2', label3='label3',title=''):
    for row,col in pxs:
        compare_pixel_dists(arr1,arr2,row,col, arr3=arr3,label1=label1,label2=label2,label3=label3,title=title)

# compare_pixel_dists_many(baseline,rx,ks_maxima[:5],label1='baseline',label2='response',title='ks')
# compare_pixel_dists_many(baseline_reg,reg,ks_maxima_reg[:5],label1='baseline',label2='response',title='ks reg')
# compare_pixel_dists_many(baseline,rx,emd_maxima[:5],label1='baseline',label2='response',title='emd')
# compare_pixel_dists_many(baseline_reg,reg,emd_maxima_reg[:5],label1='baseline',label2='response',title='emd reg')


def compare_pixel_traces(arr1,arr2,row,col, label1='baseline', label2='ext response', title=''):
    arr1, arr2 = tile2arr2(arr1[:,row,col], arr2[:,row,col])
    plt.plot(arr1, label=label1, alpha=0.7)
    plt.plot(arr2, label=label2, alpha=0.7)
    plt.legend()
    plt.title(f'{title} - row = {row}, col = {col}')
    plt.show()
def compare_pixel_traces_many(arr1,arr2,pxs,label1='arr1', label2='arr2',title=''):
    for row,col in pxs:
        compare_pixel_traces(arr1,arr2,row,col,label1=label1,label2=label2,title=title)
        
def compare_traces(arr1,row1,col1,arr2,row2,col2,
                   stimulus=[],stimulus_scale=100,
                   label1='arr1',label2='arr2',title='',
                   alpha1=0.9,alpha2=0.75,split_plots=False):
    plt.plot(arr1[:,row1,col1], label=label1, alpha=alpha1)
    plt.plot(arr2[:,row2,col2], label=label2, alpha=alpha2)
    if len(stimulus) > 0:
        plt.plot(stimulus*stimulus_scale)
    plt.legend()
    title = f'{title} - {label1} = ({row1,col1}), {label2} = ({row2, col2})'
    plt.title(title)
    plt.show()
    if split_plots:
        mk_plots([arr1[:,row1,col1], arr2[:,row2,col2]], title=title, subtitles=[label1,label2])
        plt.show()
    

# compare_pixel_traces_many(baseline,rx,ks_maxima[:5],label1='ext baseline',label2='response',title='ks')
# compare_pixel_traces_many(baseline,rx,emd_maxima[:5],label1='ext baseline',label2='response',title='emd')
# compare_pixel_dists_many(baseline_reg,reg,ks_maxima_reg[:5],label1='ext baseline',label2='response',title='ks reg')
# compare_pixel_dists_many(baseline_reg,reg,emd_map_maxima_reg[:5],label1='ext baseline',label2='response',title='emd reg')


# all together (normalized)

ks_map /= ks_map.max()
emd_map /= emd_map.max()
ks_regmap /= ks_regmap.max()
emd_regmap /= emd_regmap.max()

mk_plots([ks_map,ks_regmap,emd_map,emd_regmap],title='proj maps',
         subtitles=['ks','ks reg','emd','emd reg'],normalize=True)


# TODO GAUSS2D:
# apply 2D filter to every slice in the stack & get temp local maxima

# synapse based kernel convolution (synapse size + iGlusniffer dynamics)
print('\n 3d convolutions:')
cx = conv3d(rx)
baseline_cx = conv3d(baseline)
cx_reg = conv3d(reg)
baseline_cx_reg = conv3d(baseline_reg,)

cx_ks_map, cx_emd_map = pixel_wise_comparison(baseline_cx,cx)
cxreg_ks_map, cxreg_emd_map = pixel_wise_comparison(baseline_cx_reg,cx_reg)

mk_plots(cx_ks_map, title='cx ks map')
mk_plots(cxreg_ks_map, title='cx ks reg map')
mk_plots(cx_emd_map, title='cx emd map')
mk_plots(cxreg_emd_map, title='cx emd reg map')

ks_cx_maxima, ks_cx_mask = get_maxima(cx_ks_map, num_peaks=33, title='cx ks maxima')
ks_cx_maxima_reg, ks_cx_mask_reg = get_maxima(cxreg_ks_map, num_peaks=33, title='cx ks reg maxima')
emd_cx_maxima, emd_cx_mask = get_maxima(cx_emd_map, num_peaks=33, title='cx emd maxima')
emd_cx_maxima_reg, emd_cx_mask_reg = get_maxima(cxreg_emd_map, num_peaks=33, title='cx emd reg maxima')


# returns: shared, only in ixs1, only in ixs2
def compare_indexes(ixs1,ixs2):
    q1, q2 = [], []
    for ei, (y, x) in enumerate(ixs1):
        for ej, (yy, xx) in enumerate(ixs2):
            if y == yy and x == xx:
                q1.append(ei)
                q2.append(ej)
    pxs12 = ixs1[q1]
    nq1 = [i for i in np.arange(ixs1.shape[0]) if i not in q1]
    nq2 = [i for i in np.arange(ixs2.shape[0]) if i not in q2]
    pxs1 = ixs1[nq1]
    pxs2 = ixs2[nq2]
    return pxs12, pxs1, pxs2

ixs_shared, ixs_ks, ixs_emd = compare_indexes(ks_maxima, emd_maxima)








#