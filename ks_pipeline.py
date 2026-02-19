#!/usr/bin/env python3
# -*- coding: utf-8 -*-


from platform import system
from utils.loading import load_pxp, pxp_info
from utils.stack2stimulus import mk_step_indexes
import numpy as np
from scipy.stats import kstest, kurtosis
from scipy.stats import wasserstein_distance as emd
from skimage.feature import peak_local_max
import matplotlib.pyplot as plt
from utils.plotting_fxs import mk_plots, overlaying_imshows, simple_plot, mk_raster_plot
from utils.auxs import datapoints_in_seconds, get_max_indexes
from utils.improc import gauss1d, conv3d
from tqdm import tqdm
import seaborn as sns


# direct loading for now
if system() == 'Windows':
    # fpath = 'C:\\Users\\Fernando\\zf\\data\\jose_data\\Glutamate_Tectum\\F1_glut_HUC_AF10\\a1\\steps_pre_AF10_a1001.pxp'
    # fpath = 'C:\\Users\\Fernando\\zf\\data\\jose_data\\Glutamate_Tectum\\F1_glut_HUC_AF10\\a2\\Steps_pre_AF10_a2008.pxp'
    fpath = 'C:\\Users\\Fernando\\zf\\data\\jose_data\\Glutamate_Tectum\\F2_glut_HUC_AF10\\A1\\Steps_pre_AF10_a1015.pxp'
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
    # fpath = 'C:\\Users\\Fernando\\zf\\data\\glu_100hz\\f1\\a1\\steps_glu_1013.pxp'
    # fpath = 'C:\\Users\\Fernando\\zf\\data\\glu_100_hz\\f1\\a1\\steps_glu_1014.pxp'
    # fpath = 'C:\\Users\\Fernando\\zf\\data\\glu_100_hz\\f1\\a1\\steps_glu_1015.pxp'
    # fpath = 'C:\\Users\\Fernando\\zf\\data\\glu_100_hz\\f2\\steps_glu_1006.pxp'
    # fpath = 'C:\\Users\\Fernando\\zf\\data\\glu_100_hz\\f2\\steps_glu_1007.pxp'
    # fpath = 'C:\\Users\\Fernando\\zf\\data\\glu_100_hz\\f2\\steps_glu_1008.pxp'
    # response = tf.imread('C:\\Users\\Fernando\\zf\\data\\glu_a1\\steps_pre_AF10_a1001.tif')
    # response_reg = tf.imread('C:\\Users\\Fernando\\zf\\data\\glu_a1\\steps_pre_AF10_a1001_Ch1_reg.tif')
    # stimulus = read_itx('C:\\Users\\Fernando\\zf\\data\\glu_a1\\steps_timewave.itx')
    response, response_reg, stimulus, igor_info = load_pxp(fpath)
else:
    # fpath = '/Users/f/Dropbox/_r66y/r66xe/2p_data/jose_glu_exps/steps_AF10_a1001.pxp'
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
baseline = response[ixs_baseline]
rx = response[ixs_activity]
# same, for registered movie
baseline_reg = response_reg[ixs_baseline]
rx_reg = response_reg[ixs_activity]


#####################################################################
                # kurtosis & fano factor maps
#####################################################################

def compare_kurtosis(arr0,arr1):
    if arr1.shape[1:] != arr0.shape[1:]:
        raise Exception('arrays have different shapes!')
    kurmap = np.zeros((arr1.shape[1:]))
    for row in tqdm(range(arr1.shape[1])):
        for col in range(arr1.shape[2]):
            kur0 = kurtosis(arr0[:,row,col])
            kur1 = kurtosis(arr1[:,row,col])
            kurmap[row,col] = (kur1-kur0)/(kur1+kur0)
    rx,cx = np.where(kurmap==kurmap.max())
    maxs = get_max_indexes(kurmap,3)
    for ri,ci in maxs:
        sns.distplot(arr0[:,ri,ci], label='baseline')
        sns.distplot(arr1[:,ri,ci], label='response')
        plt.legend()
        plt.title(f'kurtosis comparison, loc: {ri}, {ci}')
        plt.show()
    return kurmap

rx_kurmap = compare_kurtosis(baseline,rx)
# rx_reg_kurmap, rx_reg_ffmap = compare_kurtosis(baseline_reg,rx_reg)

simple_plot(rx_kurmap, title='kurtosis map', mk_cbar=True)
# simple_plot(rx_reg_kurmap, title='kurtosis reg map', mk_cbar=True)

#####################################################################
                    # image substraction
#####################################################################    

response_sub = np.abs(response - response.mean(axis=0))
simple_plot(response_sub.mean(axis=0), mk_cbar=True, title='background substraction')

response_reg_sub = np.abs(response_reg - response.mean(axis=0))
simple_plot(response_reg_sub.mean(axis=0), mk_cbar=True, title='background substraction reg')

rx_sub = np.abs(rx - baseline.mean(axis=0))
simple_plot(rx_sub.mean(axis=0), mk_cbar=True, title='background substraction act/base')

rx_reg_sub = np.abs(rx_reg - baseline_reg.mean(axis=0))
simple_plot(rx_reg_sub.mean(axis=0), mk_cbar=True, title='background substraction reg act/base')


#####################################################################
                    # make mappings
#####################################################################

# mk pixel-wise map of difference between distributions using ks-method
def pixel_wise_comparison(arr1,arr2):
    print('\npixel wise comparison: ks-map - emd-map - ff map')
    if arr1.shape[1:] != arr2.shape[1:]:
        raise Exception('comparing apples with pears? (arrays have different dimensions)')
    nframes,rows,cols = arr1.shape
    ksmap = np.zeros((rows, cols))
    emdmap = np.zeros((rows, cols))
    ffmap = np.zeros((rows, cols))
    for row in tqdm(range(rows)):
        for col in range(cols):
            ri = arr2[:,row,col]
            x = kstest(arr1[:,row,col], ri)
            ksmap[row,col] = x.statistic
            emdmap[row,col] = emd(arr1[:,row,col], ri)
            ffmap[row,col] = ri.var() / ri.mean()
    ffmap = np.nan_to_num(ffmap,0)
    return ksmap, emdmap, ffmap

ks_map, emd_map, ff_map = pixel_wise_comparison(baseline,rx)
ks_reg_map, emd_reg_map, ff_reg_map = pixel_wise_comparison(baseline_reg,rx_reg)
ks_sub_map, emd_sub_map, ff_sub_map = pixel_wise_comparison(baseline,rx_sub)
ks_reg_sub_map, emd_reg_sub_map, ff_reg_sub_map = pixel_wise_comparison(baseline_reg,rx_reg_sub)

simple_plot(ks_map, title='ks map', mk_cbar=True)
simple_plot(ks_reg_map, title='ks reg map', mk_cbar=True)
simple_plot(ks_sub_map, title='ks sub map', mk_cbar=True)
simple_plot(ks_reg_sub_map, title='ks reg sub map', mk_cbar=True)

simple_plot(emd_map, title='emd map', mk_cbar=True)
simple_plot(emd_reg_map, title='emd reg map', mk_cbar=True)
simple_plot(emd_sub_map, title='emd sub map', mk_cbar=True)
simple_plot(emd_reg_sub_map, title='emd reg sub map', mk_cbar=True)

simple_plot(ff_map, title='ff map', mk_cbar=True)
simple_plot(ff_reg_map, title='ff reg map', mk_cbar=True)
simple_plot(ff_sub_map, title='ff sub map', mk_cbar=True)
simple_plot(ff_reg_sub_map, title='ff reg sub map', mk_cbar=True)


#####################################################################
                    # band pass filter
#####################################################################





#####################################################################
                    # get maxima
#####################################################################

# look for maxima
def get_maxima(arr, min_distance=1, num_peaks=50,title=''):
    maxima = peak_local_max(arr, min_distance=min_distance, num_peaks=num_peaks)
    mask = np.zeros((arr.shape))
    for mr,mc in maxima:
        mask[mr,mc] = arr[mr,mc]
    title = f'{title} - maxima={num_peaks}'
    # overlaying_imshows(arr, mask, title=title)
    overlaying_imshows(response.mean(axis=0), mask, title=title)
    return maxima, mask

npeaks=41
ks_maxima, ks_mask = get_maxima(ks_map, num_peaks=npeaks, title='ks maxima')
ks_reg_maxima, ks_reg_mask = get_maxima(ks_reg_map, num_peaks=npeaks, title='ks reg maxima')
ks_sub_maxima, ks_sub_mask = get_maxima(ks_sub_map, num_peaks=npeaks, title='ks sub maxima')
ks_reg_sub_maxima, ks_reg_sub_mask = get_maxima(ks_reg_sub_map, num_peaks=npeaks, title='ks reg sub maxima')

emd_maxima, emd_mask = get_maxima(emd_map, num_peaks=npeaks, title='emd maxima')
emd_reg_maxima, emd_reg_mask = get_maxima(emd_reg_map, num_peaks=npeaks, title='emd reg maxima')
emd_sub_maxima, emd_sub_mask = get_maxima(emd_sub_map, num_peaks=npeaks, title='emd sub maxima')
emd_reg_sub_maxima, emd_reg_sub_mask = get_maxima(emd_reg_sub_map, num_peaks=npeaks, title='emd reg sub maxima')

ff_maxima, ff_mask = get_maxima(ff_map, num_peaks=npeaks, title='ff maxima')
ff_reg_maxima, ff_reg_mask = get_maxima(ff_reg_map, num_peaks=npeaks, title='ff reg maxima')
ff_sub_maxima, ff_sub_mask = get_maxima(ff_sub_map, num_peaks=npeaks, title='ff sub maxima')
ff_reg_sub_maxima, ff_reg_sub_mask = get_maxima(ff_reg_sub_map, num_peaks=npeaks, title='ff reg sub maxima')

#####################################################################
                    # compare: raster plots
#####################################################################

# def mk_raster_plot(arr, locs, title='', mk_cbar=True):
#     raster = np.zeros((locs.shape[0],arr.shape[0]))
#     for ei,(row,col) in enumerate(locs):
#         raster[ei] = arr[:,row,col]
#     simple_plot(raster, mk_cbar=mk_cbar, title=title, aspect='auto')
#     return raster

stim = stimulus[100:-100]
ks_raster = mk_raster_plot(rx, ks_maxima, stimulus=stim, title='ks')
ks_reg_raster = mk_raster_plot(rx_reg, ks_reg_maxima, stimulus=stim, title='ks reg')
ks_sub_raster = mk_raster_plot(rx_sub, ks_sub_maxima, stimulus=stim, title='ks sub')
ks_reg_sub_raster = mk_raster_plot(rx_reg_sub, ks_maxima, stimulus=stim, title='ks reg sub')

emd_raster = mk_raster_plot(rx, emd_maxima, stimulus=stim, title='emd')
emd_reg_raster = mk_raster_plot(rx_reg, emd_reg_maxima, stimulus=stim, title='emd reg')
emd_sub_raster = mk_raster_plot(rx_sub, emd_sub_maxima, stimulus=stim, title='emd sub')
emd_reg_sub_raster = mk_raster_plot(rx_reg_sub, emd_reg_sub_maxima, stimulus=stim, title='emd reg sub')

emd_raster = mk_raster_plot(rx, ff_maxima, stimulus=stim, title='ff')
emd_reg_raster = mk_raster_plot(rx_reg, ff_reg_maxima, stimulus=stim, title='ff reg')
emd_sub_raster = mk_raster_plot(rx_sub, ff_sub_maxima, stimulus=stim, title='ff sub')
emd_reg_sub_raster = mk_raster_plot(rx_reg_sub, ff_reg_sub_maxima, stimulus=stim, title='ff reg sub')

#### plus baseline
stim = stimulus
ks_raster = mk_raster_plot(response, ks_maxima, stimulus=stim, title='ks')
ks_reg_raster = mk_raster_plot(response_reg, ks_reg_maxima, stimulus=stim, title='ks reg')
ks_sub_raster = mk_raster_plot(response_sub, ks_sub_maxima, stimulus=stim, title='ks sub')
ks_reg_sub_raster = mk_raster_plot(response_reg_sub, ks_maxima, stimulus=stim, title='ks reg sub')

emd_raster = mk_raster_plot(response, emd_maxima, stimulus=stim, title='emd')
emd_reg_raster = mk_raster_plot(response_reg, emd_reg_maxima, stimulus=stim, title='emd reg')
emd_sub_raster = mk_raster_plot(response_sub, emd_sub_maxima, stimulus=stim, title='emd sub')
emd_reg_sub_raster = mk_raster_plot(response_reg_sub, emd_reg_sub_maxima, stimulus=stim, title='emd reg sub')

emd_raster = mk_raster_plot(response, ff_maxima, stimulus=stim, title='ff')
emd_reg_raster = mk_raster_plot(response_reg, ff_reg_maxima, stimulus=stim, title='ff reg')
emd_sub_raster = mk_raster_plot(response_sub, ff_sub_maxima, stimulus=stim, title='ff sub')
emd_reg_sub_raster = mk_raster_plot(response_reg_sub, ff_reg_sub_maxima, stimulus=stim, title='ff reg sub')



#####################################################################
                    # 3d synapse-based 
#####################################################################






#####################################################################
                    # compare: traces
#####################################################################



def compare_best_traces(resp,locs,subtitles=[],title='',npeaks=1):
    for i in range(npeaks):
        traces = []
        peaks = [loc[i] for loc in locs]
        subt_plus = []
        for ei,(mrow,mcol) in enumerate(peaks):
            traces.append(resp[:,mrow,mcol])
            subt_plus.append(f'{subtitles[ei]} - row={mrow}, col={mcol}')
        title_plus = f'{title} best = {subtitles[i]}'
        mk_plots(iims=traces, subtitles=subt_plus, rows=len(locs), cols=1, title=title_plus)

compare_best_traces(response,[ks_maxima,emd_maxima,ff_maxima,ff_maxima], subtitles=['ks','emd','ff','x'],title='response')
compare_best_traces(response,[ks_reg_maxima,emd_reg_maxima,ff_reg_maxima,ff_maxima], subtitles=['ks','emd','ff','x'],title='reg')
compare_best_traces(response,[ks_sub_maxima,emd_sub_maxima,ff_sub_maxima,ff_maxima], subtitles=['ks','emd','ff','x'],title='sub')
compare_best_traces(response,[ks_reg_sub_maxima,emd_reg_sub_maxima,ff_reg_sub_maxima,ff_maxima], subtitles=['ks','emd','ff','x'],title='reg sub')

























































#
