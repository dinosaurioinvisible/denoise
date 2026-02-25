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
from utils.auxs import datapoints_in_seconds, get_max_indexes, compare_indexes
from filters import fiji_fft_bandpass_anisotropic as fft
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
    # fpath = '/Users/f/Dropbox/_r66y/r66xe/2p_data/jose_glu_exps/Steps_pre_AF10_a1014.pxp'
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
                            # params
#####################################################################

# band pass filter
fft_in = 3
fft_out = 40
# maxima
npeaks = 0
percetile = 60
# for raster plots
plot_baseline = True

#####################################################################
                # kurtosis & fano factor maps
#####################################################################

def compare_kurtosis(arr0,arr1,n=5):
    if arr1.shape[1:] != arr0.shape[1:]:
        raise Exception('arrays have different shapes!')
    kurmap = np.zeros((arr1.shape[1:]))
    for row in tqdm(range(arr1.shape[1])):
        for col in range(arr1.shape[2]):
            kur0 = kurtosis(arr0[:,row,col])
            kur1 = kurtosis(arr1[:,row,col])
            kurmap[row,col] = (kur1-kur0)/(abs(kur1)+abs(kur0))
    rx,cx = np.where(kurmap==kurmap.max())
    maxs = get_max_indexes(kurmap,n)
    for ri,ci in maxs:
        sns.distplot(arr0[:,ri,ci], label='baseline')
        sns.distplot(arr1[:,ri,ci], label='response')
        plt.legend()
        val = kurmap[ri][ci]
        plt.title(f'Kurtosis - loc: ({ri},{ci}), (ka-kb)/(ka+kb)={val:.2f}')
        plt.show()
    kurmap = np.where(kurmap<0,0,kurmap)
    return kurmap

# rx_kurmap = compare_kurtosis(baseline,rx,n=4)
# rx_reg_kurmap, rx_reg_ffmap = compare_kurtosis(baseline_reg,rx_reg)

# simple_plot(rx_kurmap, title='kurtosis map', mk_cbar=True)
# simple_plot(rx_reg_kurmap, title='kurtosis reg map', mk_cbar=True)


#####################################################################
                    # background substraction
#####################################################################    

response_sub = np.abs(response - response.mean(axis=0))
# simple_plot(response_sub.mean(axis=0), mk_cbar=True, title='background substraction')

response_reg_sub = np.abs(response_reg - response.mean(axis=0))
# simple_plot(response_reg_sub.mean(axis=0), mk_cbar=True, title='background substraction reg')

rx_sub = np.abs(rx - baseline.mean(axis=0))
# simple_plot(rx_sub.mean(axis=0), mk_cbar=True, title='background substraction act/base')

rx_reg_sub = np.abs(rx_reg - baseline_reg.mean(axis=0))
# simple_plot(rx_reg_sub.mean(axis=0), mk_cbar=True, title='background substraction reg act/base')

# mk_plots([response_sub.mean(axis=0),response_reg_sub.mean(axis=0),
#           rx_sub.mean(axis=0),rx_reg_sub.mean(axis=0)],
#          subtitles=['trial sub','trial reg sub','activity sub','activity reg sub'],
#          title='background substraction')


#####################################################################
                    # make mappings (ks, emd, ff)
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
# ks_sub_map, emd_sub_map, ff_sub_map = pixel_wise_comparison(baseline,rx_sub)
# ks_reg_sub_map, emd_reg_sub_map, ff_reg_sub_map = pixel_wise_comparison(baseline_reg,rx_reg_sub)

simple_plot(ks_map, title='ks map', mk_cbar=True)
simple_plot(ks_reg_map, title='ks reg map', mk_cbar=True)
# simple_plot(ks_sub_map, title='ks sub map', mk_cbar=True)
# simple_plot(ks_reg_sub_map, title='ks reg sub map', mk_cbar=True)

simple_plot(emd_map, title='emd map', mk_cbar=True)
simple_plot(emd_reg_map, title='emd reg map', mk_cbar=True)
# simple_plot(emd_sub_map, title='emd sub map', mk_cbar=True)
# simple_plot(emd_reg_sub_map, title='emd reg sub map', mk_cbar=True)

simple_plot(ff_map, title='ff map', mk_cbar=True)
simple_plot(ff_reg_map, title='ff reg map', mk_cbar=True)
# simple_plot(ff_sub_map, title='ff sub map', mk_cbar=True)
# simple_plot(ff_reg_sub_map, title='ff reg sub map', mk_cbar=True)

#####################################################################
                    # 3d synapse-based 
#####################################################################



#####################################################################
                    # band pass filter
#####################################################################

# ks_map_fft = fft(ks_map,dx=data['pixel_dx'],dy=data['pixel_dy'],filter_small=fft_in,filter_large=fft_out)
# ks_map_fft = np.where(ks_map_fft<0,0,ks_map_fft)
# simple_plot(ks_map_fft, mk_cbar=True, title=f'ks map fft bandpass; min={fft_in}, max={fft_out}')

ks_reg_map_fft = fft(ks_reg_map,dx=data['pixel_dx'],dy=data['pixel_dy'],filter_small=fft_in,filter_large=fft_out)
ks_reg_map_fft = np.where(ks_reg_map_fft<0,0,ks_reg_map_fft)
simple_plot(ks_reg_map_fft, mk_cbar=True, title=f'ks reg map fft bandpass; min={fft_in}, max={fft_out}')

# emd_map_fft = fft(emd_map,dx=data['pixel_dx'],dy=data['pixel_dy'],filter_small=fft_in,filter_large=fft_out)
# emd_map_fft = np.where(emd_map_fft<0,0,emd_map_fft)
# simple_plot(emd_map_fft, mk_cbar=True, title=f'emd map fft bandpass; min={fft_in}, max={fft_out}')

emd_reg_map_fft = fft(emd_reg_map,dx=data['pixel_dx'],dy=data['pixel_dy'],filter_small=fft_in,filter_large=fft_out)
emd_reg_map_fft = np.where(emd_reg_map_fft<0,0,ks_reg_map_fft)
simple_plot(emd_reg_map_fft, mk_cbar=True, title=f'emd reg map fft bandpass; min={fft_in}, max={fft_out}')

# ff_map_fft = fft(ff_map,dx=data['pixel_dx'],dy=data['pixel_dy'],filter_small=fft_in,filter_large=fft_out)
# ff_map_fft = np.where(ff_map_fft<0,0,ff_map_fft)
# simple_plot(ff_map_fft, mk_cbar=True, title=f'ff map fft bandpass; min={fft_in}, max={fft_out}')

ff_reg_map_fft = fft(ks_reg_map,dx=data['pixel_dx'],dy=data['pixel_dy'],filter_small=fft_in,filter_large=fft_out)
ff_reg_map_fft = np.where(ff_reg_map_fft<0,0,ff_reg_map_fft)
simple_plot(ff_reg_map_fft, mk_cbar=True, title=f'ks reg map fft bandpass; min={fft_in}, max={fft_out}')


#####################################################################
                    # get maxima
#####################################################################

# look for maxima
def get_maxima(arr, min_distance=1, num_peaks=0, percentile = 60, title=''):
    if num_peaks:
        maxima = peak_local_max(arr, min_distance=min_distance, num_peaks=num_peaks)
    else:
        maxima = peak_local_max(arr, min_distance=min_distance, threshold_abs=percentile)
    mask = np.zeros((arr.shape))
    for mr,mc in maxima:
        mask[mr,mc] = arr[mr,mc]
    title = f'{title} - maxima={num_peaks}'
    # overlaying_imshows(arr, mask, title=title)
    overlaying_imshows(response.mean(axis=0), mask, title=title)
    return maxima, mask

# ks_maxima, ks_mask = get_maxima(ks_map, num_peaks=npeaks, title='ks maxima')
ks_reg_maxima, ks_reg_mask = get_maxima(ks_reg_map, num_peaks=npeaks, title='ks reg maxima')
# ks_sub_maxima, ks_sub_mask = get_maxima(ks_sub_map, num_peaks=npeaks, title='ks sub maxima')
# ks_reg_sub_maxima, ks_reg_sub_mask = get_maxima(ks_reg_sub_map, num_peaks=npeaks, title='ks reg sub maxima')
# ks_fft_maxima, ks_fft_mask = get_maxima(ks_map_fft, num_peaks=npeaks, title='ks fft maxima')
ks_fft_reg_maxima, ks_fft_reg_mask = get_maxima(ks_reg_map_fft, num_peaks=npeaks, title='ks fft reg maxima')

# emd_maxima, emd_mask = get_maxima(emd_map, num_peaks=npeaks, title='emd maxima')
emd_reg_maxima, emd_reg_mask = get_maxima(emd_reg_map, num_peaks=npeaks, title='emd reg maxima')
# emd_sub_maxima, emd_sub_mask = get_maxima(emd_sub_map, num_peaks=npeaks, title='emd sub maxima')
# emd_reg_sub_maxima, emd_reg_sub_mask = get_maxima(emd_reg_sub_map, num_peaks=npeaks, title='emd reg sub maxima')
# emd_fft_maxima, emd_mask = get_maxima(emd_map_fft, num_peaks=npeaks, title='emd fft maxima')
emd_reg_fft_maxima, emd_reg_fft_mask = get_maxima(emd_reg_map_fft, num_peaks=npeaks, title='emd reg fft maxima')

# ff_maxima, ff_mask = get_maxima(ff_map, num_peaks=npeaks, title='ff maxima')
ff_reg_maxima, ff_reg_mask = get_maxima(ff_reg_map, num_peaks=npeaks, title='ff reg maxima')
# ff_sub_maxima, ff_sub_mask = get_maxima(ff_sub_map, num_peaks=npeaks, title='ff sub maxima')
# ff_reg_sub_maxima, ff_reg_sub_mask = get_maxima(ff_reg_sub_map, num_peaks=npeaks, title='ff reg sub maxima')
# ff_fft_maxima, emd_mask = get_maxima(ff_map_fft, num_peaks=npeaks, title='ff fft maxima')
ff_reg_fft_maxima, ff_reg_fft_mask = get_maxima(ff_reg_map_fft, num_peaks=npeaks, title='emd reg fft maxima')


#####################################################################
                    # 2d gaussians 
#####################################################################



#####################################################################
                    # check different points 
#####################################################################

ixs_ks_emd, ixs_only_ks_emd, ixs_only_emd = compare_indexes(ks_reg_maxima, emd_reg_maxima)
ixs_ff_emd, ixs_only_ks_ff, ixs_only_ff = compare_indexes(ks_reg_maxima, ff_reg_maxima)



#####################################################################
                    # compare: raster plots
#####################################################################

# def mk_raster_plot(arr, locs, title='', mk_cbar=True):
#     raster = np.zeros((locs.shape[0],arr.shape[0]))
#     for ei,(row,col) in enumerate(locs):
#         raster[ei] = arr[:,row,col]
#     simple_plot(raster, mk_cbar=mk_cbar, title=title, aspect='auto')
#     return raster

if not plot_baseline:
    stim = stimulus[100:-100]
    # ks_raster = mk_raster_plot(rx, ks_maxima, stimulus=stim, title='ks')
    ks_reg_raster = mk_raster_plot(rx_reg, ks_reg_maxima, stimulus=stim, title='ks reg')
    # ks_sub_raster = mk_raster_plot(rx_sub, ks_sub_maxima, stimulus=stim, title='ks sub')
    # ks_reg_sub_raster = mk_raster_plot(rx_reg_sub, ks_maxima, stimulus=stim, title='ks reg sub')
    
    # ks_fft_raster = mk_raster_plot(rx, ks_fft_maxima, stimulus=stim, title='ks fft')
    ks_fft_reg_raster = mk_raster_plot(rx, ks_fft_reg_maxima, stimulus=stim, title='ks reg fft')
    
    # emd_raster = mk_raster_plot(rx, emd_maxima, stimulus=stim, title='emd')
    emd_reg_raster = mk_raster_plot(rx_reg, emd_reg_maxima, stimulus=stim, title='emd reg')
    # emd_sub_raster = mk_raster_plot(rx_sub, emd_sub_maxima, stimulus=stim, title='emd sub')
    # emd_reg_sub_raster = mk_raster_plot(rx_reg_sub, emd_reg_sub_maxima, stimulus=stim, title='emd reg sub')
    
    # ff_raster = mk_raster_plot(rx, ff_maxima, stimulus=stim, title='ff')
    ff_reg_raster = mk_raster_plot(rx_reg, ff_reg_maxima, stimulus=stim, title='ff reg')
    # ff_sub_raster = mk_raster_plot(rx_sub, ff_sub_maxima, stimulus=stim, title='ff sub')
    # ff_reg_sub_raster = mk_raster_plot(rx_reg_sub, ff_reg_sub_maxima, stimulus=stim, title='ff reg sub')

else:
    #### plus baseline
    stim = stimulus
    # ks_raster = mk_raster_plot(response, ks_maxima, stimulus=stim, title='ks')
    ks_reg_raster = mk_raster_plot(response_reg, ks_reg_maxima, stimulus=stim, title='ks reg')
    # ks_sub_raster = mk_raster_plot(response_sub, ks_sub_maxima, stimulus=stim, title='ks sub')
    # ks_reg_sub_raster = mk_raster_plot(response_reg_sub, ks_reg_sub_maxima, stimulus=stim, title='ks reg sub')
    
    # TODO: this strangely really good, why?
    # ks_reg_sub_raster = mk_raster_plot(response_reg_sub, ks_maxima, stimulus=stim, title='ks reg sub')
    
    # ks_fft = mk_raster_plot(response_reg_sub, ks_maxima, stimulus=stim, title='ks reg sub')
    
    # emd_raster = mk_raster_plot(response, emd_maxima, stimulus=stim, title='emd')
    emd_reg_raster = mk_raster_plot(response_reg, emd_reg_maxima, stimulus=stim, title='emd reg')
    # emd_sub_raster = mk_raster_plot(response_sub, emd_sub_maxima, stimulus=stim, title='emd sub')
    # emd_reg_sub_raster = mk_raster_plot(response_reg_sub, emd_reg_sub_maxima, stimulus=stim, title='emd reg sub')
    
    # ff_raster = mk_raster_plot(response, ff_maxima, stimulus=stim, title='ff')
    ff_reg_raster = mk_raster_plot(response_reg, ff_reg_maxima, stimulus=stim, title='ff reg')
    # ff_sub_raster = mk_raster_plot(response_sub, ff_sub_maxima, stimulus=stim, title='ff sub')
    # ff_reg_sub_raster = mk_raster_plot(response_reg_sub, ff_reg_sub_maxima, stimulus=stim, title='ff reg sub')


#####################################################################
                    # compare: traces
#####################################################################


def compare_best_traces(resp,arr1,arr2,arr3,arr4,
                        px1=[],px2=[],px3=[],px4=[],
                        subtitles=['','','',''],
                        title=''):
    traces = []
    subs = []
    if len(px1) == 0:
        px1 = get_max_indexes(arr1,n=1)[0]
    if len(px2) == 0:
        px2 = get_max_indexes(arr2,n=1)[0]
    if len(px3) == 0:
        px3 = get_max_indexes(arr3,n=1)[0]
    if len(px4) == 0:
        px4 = get_max_indexes(arr4,n=1)[0]
    for ei,(mrow,mcol) in enumerate([px1,px2,px3,px4]):
        traces.append(resp[:,mrow,mcol])
        subs.append(f'{subtitles[ei]} - row={mrow}, col={mcol}')
    mk_plots(iims=traces, subtitles=subs, rows=len(traces), cols=1, title=title)
    
def multiple_best_traces(resp,arr1,arr2,arr3,arr4,n=5,subtitles=[],title=''):
    maxs1 = get_max_indexes(arr1,n=n)
    maxs2 = get_max_indexes(arr2,n=n)
    maxs3 = get_max_indexes(arr3,n=n)
    maxs4 = get_max_indexes(arr4,n=n)
    for i in range(n):
        compare_best_traces(response,arr1,arr2,arr3,arr4, 
                            px1=maxs1[i], px2=maxs2[i], px3=maxs3[i], px4=maxs4[i],
                            subtitles=subtitles,
                            title=title)
    
# multiple_best_traces(response,ks_map,ks_reg_map,ks_sub_map,ks_map_fft, subtitles=['ks','ks reg','ks sub','ks fft'],title='ks projection')
# multiple_best_traces(response,emd_map,emd_reg_map,emd_sub_map,emd_map_fft, subtitles=['emd','emd reg','emd sub','emd fft'],title='emd projection')
# multiple_best_traces(response,ff_map,ff_reg_map,ff_sub_map,ff_map_fft, subtitles=['ff','ff reg','ff sub','ff fft'],title='fano factor')

multiple_best_traces(response,ks_reg_map,emd_reg_map,ff_reg_map,ks_reg_map_fft, subtitles=['ks reg','emd reg','ff reg','ks reg fft'],title='dif projections')























































#
