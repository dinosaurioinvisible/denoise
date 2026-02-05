
import os
from auxs import read_itx
import tifffile as tf
import numpy as np
import matplotlib.pyplot as plt
from platform import system
import seaborn as sns
from tqdm import tqdm
from loading import load_pxp
from stack2stimulus import mk_step_indexes
from scipy.stats import kstest, kurtosis
from scipy.stats import wasserstein_distance as emd

if system() == 'Windows':
    # response, response_reg, stimulus = load_pxp('C:\\Users\\Fernando\\zf\\data\\jose_data\\Glutamate_Tectum\\F1_glut_HUC_AF10\\a1\\steps_pre_AF10_a1001.pxp')
    response, response_reg, stimulus = load_pxp('C:\\Users\\Fernando\\zf\\data\\jose_data\\Glutamate_Tectum\\F1_glut_HUC_AF10\\a2\\Steps_pre_AF10_a2008.pxp')
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
    # fpath = '/Users/f/Dropbox/_r66y/r66xe/2p_data/jose_glu_exps/steps_pre_af10_a1001.pxp'
    # fpath = '/Users/f/Dropbox/_r66y/r66xe/2p_data/jose_glu_exps/Steps_pre_AF10_a2008.pxp'
    fpath = '/Users/f/Dropbox/_r66y/r66xe/2p_data/jose_glu_exps/Steps_pre_AF10_a1015.pxp'
    response, response_reg, stimulus = load_pxp(fpath)


print()
# msPerLine = samples / number of lines / number of frames
msPerLine = stimulus.size/response.shape[1]/response.shape[0]
msPerFrame = msPerLine * response.shape[1]
frPerSec = 1000/msPerFrame
print(f'msPerLine = {msPerLine}, msPerFrame = {msPerFrame}')
print(f'sampling rate = {frPerSec} Hz')
# sanity check: get response freq => sample_freq = msPerFrame
sample_freq = stimulus.shape[0]/response.shape[0]
print(f'stimulus points = {stimulus.size}')
print(f'response datapoints = {response.shape[0]}')
print(f'1 sample every: {sample_freq} stimulus points: ')
# match stimulus to every sampling point. *100 is for plotting
stimulus_scaled = stimulus[::int(sample_freq)]*100

# match response & stimulus data
# returns indexes for frames
steps, ixs00, ixs01, ixs12, ixs21, ixs10 = mk_step_indexes(stimulus, msPerFrame, delta=0.5)

# slice stack into components: base
tx00 = response*0
rx00 = response[ixs00]
tx00[ixs00] = response[ixs00]
# low > base
tx01 = response*0
rx01 = response[ixs01]
tx01[ixs01] = response[ixs01]
# base > high
tx12 = response*0
rx12 = response[ixs12]
tx12[ixs12] = response[ixs12]
# high > base
tx21 = response*0
rx21 = response[ixs21]
tx21[ixs21] = response[ixs21]
# base > low
tx10 = response*0
rx10 = response[ixs10]
tx10[ixs10] = response[ixs10]




######################################################
                # simple sum
######################################################

def mk_pixel_sum_map(arr,arr0=[],title='',mk_plots=True):
    rows = 50
    cols = 128
    psmap = np.zeros((rows,cols))
    for row in range(rows):
        for col in range(cols):
            psmap[row,col] = np.sum(arr[:,row,col])
    if mk_plots:
        im = plt.imshow(psmap)
        plt.title(f'{title}')
        plt.colorbar(im, orientation='horizontal')
        plt.show()
        if len(arr0) > 0:
            deltamap = arr.sum(axis=0) - arr0.sum(axis=0)
            plt.imshow(deltamap)
            plt.title(f'{title} subs')
            plt.show()
    return psmap

smap00 = mk_pixel_sum_map(rx00,title='00')
smap01 = mk_pixel_sum_map(rx01, rx00, title='01')
smap12 = mk_pixel_sum_map(rx12, rx00, title='12')
smap21 = mk_pixel_sum_map(rx21, rx00, title='21')
smap10 = mk_pixel_sum_map(rx10, rx00, title='10')


######################################################
            # some helper fxs
######################################################

def plot_vs(arr,row,col,title=''):
    plt.plot(response[:,row,col])
    plt.plot(arr[:,row,col])
    plt.plot(stimulus_scaled)*10
    if title:
        plt.title(title)
    else:
        plt.title(f'superimposed signals row={row}, col={col}')
    plt.show()


def check_distributions(n=5):
    for _ in range(n):
        row = np.random.randint(0,50)
        col = np.random.randint(0,120)
        # kurtosis
        k00 = kurtosis(rx00[:,row,col])
        k01 = kurtosis(rx01[:,row,col])
        k12 = kurtosis(rx12[:,row,col])
        k21 = kurtosis(rx21[:,row,col])
        k10 = kurtosis(rx10[:,row,col])
        # emd X21[:,row,col])
        e01 = emd(rx00[:,row,col],rx01[:,row,col])
        e12 = emd(rx00[:,row,col],rx12[:,row,col])
        e21 = emd(rx00[:,row,col],rx21[:,row,col])
        e10 = emd(rx00[:,row,col],rx10[:,row,col])
        # histograms
        sns.distplot(rx00[:,row,col], label=f'00 - kur:{k00:.2f}')
        sns.distplot(rx01[:,row,col], label=f'01 - kur:{k01:.2f}, emd:{e01:.2f}')
        sns.distplot(rx12[:,row,col], label=f'12 - kur:{k12:.2f}, emd:{e12:.2f}')
        sns.distplot(rx21[:,row,col], label=f'21 - kur:{k21:.2f}, emd:{e21:.2f}')
        sns.distplot(rx10[:,row,col], label=f'10 - kur:{k10:.2f}, emd:{e10:.2f}')
        plt.legend()
        plt.title(f'row = {row}, col = {col}')
        plt.show()
        if e01 > 50:
            plot_vs(tx01,row,col)
        elif e12 > 50:
            plot_vs(tx12,row,col)
        elif e21 > 75:
            plot_vs(tx21,row,col)
        elif e10 > 150:
            plot_vs(tx10,row,col)
            
            
def compare_dists(dists, title=''):
    dx01, dx12, dx21, dx10 = dists
    sns.distplot(dx01, label='01')
    sns.distplot(dx12, label='12')
    sns.distplot(dx21, label='21')
    sns.distplot(dx10, label='10')
    plt.legend()
    plt.title(title)
    plt.show()


######################################################
                # ks.statistic
######################################################


def compare_ks(d1,d2,rows=50,cols=128,title='',mk_cbar=True):
    cmap = np.zeros((50,128))
    for row in tqdm(range(rows)):
        for col in range(cols):
            x = kstest(d1[:,row,col],d2[:,row,col])
            cmap[row][col] = x.statistic
    if mk_cbar:
        im = plt.imshow(cmap)
        plt.colorbar(im, orientation='horizontal')
    else:
        plt.imshow(cmap)
    plt.title(title)
    plt.show()
    return cmap

# ks01 = compare_ks(rx00,rx01, title='ks 01/base')
# ks12 = compare_ks(rx00,rx12, title='ks 12/base')
# ks21 = compare_ks(rx00,rx21, title='ks 21/base')
# ks10 = compare_ks(rx00,rx10, title='ks 10/base')
# compare_dists([ks01,ks12,ks21,ks10], title='histograms of ks test results')



######################################################
                # sliding window
######################################################

# sliding window
def compare_sw(x1,x2,wsize=2,title=''):
    rows, cols = x1.shape[1:]
    wmap = np.zeros((rows,cols))
    for i in tqdm(range(1,rows-1,wsize)):
        for j in range(1,cols-1,wsize):
            w1 = x1[:,i-1:i+1,j-1:j+1].mean(axis=(1,2))
            w2 = x2[:,i-1:i+1,j-1:j+1].mean(axis=(1,2))
            dx = kstest(w1,w2)
            wmap[i-1:i+1,j-1:j+1] = dx.statistic
    plt.imshow(wmap)
    plt.title(title)
    plt.show()
    return wmap

# sw01 = compare_sw(rx00,rx01, title='sw 01/base')
# sw12 = compare_sw(rx00,rx12, title='sw 12/base')
# sw21 = compare_sw(rx00,rx21, title='sw 21/base')
# sw10 = compare_sw(rx00,rx10, title='sw 10/base')
# compare_dists([sw01,sw12,sw21,sw10], title='histograms of sliding window test results')



######################################################
                # emd & tensor emd
######################################################

def compare_emd(d1,d2,rows=50,cols=128,title='',mk_cbar=True):
    cmap = np.zeros((50,128))
    for row in tqdm(range(rows)):
        for col in range(cols):
            cmap[row][col] = emd(d1[:,row,col],d2[:,row,col])
    if mk_cbar:
        im = plt.imshow(cmap)
        plt.colorbar(im, orientation='horizontal')
    else:
        plt.imshow(cmap)
    plt.title(title)
    plt.show()
    return cmap

emd01 = compare_emd(rx00,rx01, title='emd 01/base')
emd12 = compare_emd(rx00,rx12, title='emd 12/base')
emd21 = compare_emd(rx00,rx21, title='emd 21/base')
emd10 = compare_emd(rx00,rx10, title='emd 10/base')
compare_dists([emd01,emd12,emd21,emd10], title='histograms of emd test results')


# temd01 = compare_emd(tx00,tx01, title='tx emd 01/base')
# temd12 = compare_emd(tx00,tx12, title='tx emd 12/base')
# temd21 = compare_emd(tx00,tx21, title='tx emd 21/base')
# temd10 = compare_emd(tx00,tx10, title='tx emd 10/base')
# compare_dists([temd01,temd12,temd21,temd10], title='histograms of tensor emd test results')



######################################################
                # emd eval
######################################################

# evaluates highest cmap points
def eval_cmap(cmap,tx,rx,threshold=100,mk_plots=True):
    rows, cols = np.where(cmap > threshold)
    # sort pixels by value - if pixel mean > base mean
    pxs = sorted([[row,col,cmap[row][col]] for row,col in zip(rows,cols) if rx[:,row,col].mean() > rx00[:,row,col].mean()], key=lambda x:x[2], reverse=True)    
    mask = np.zeros((cmap.shape)).astype(int)
    for ei, (row,col,val) in enumerate(pxs):
        print(f'{ei+1} - row={row}, col={col}, val={val:.2f}')
        if mk_plots:
            plot_vs(tx,row,col,title=f'row={row}, col={col}, val={val:.2f}')
        mask[row][col] = 1
    rows,cols = np.where(mask==1)
    for row,col in zip(rows,cols):
        mask[max(0,row-1):row+2,max(0,col-1):col+2] = 1
    if mk_plots:
        masked_cmap = cmap * mask
        plt.imshow(masked_cmap)
    return mask

mask01 = eval_cmap(emd01,tx01,rx01,threshold=300)
# mask12 = eval_cmap(emd12,tx12,rx12,threshold=300)
# mask21 = eval_cmap(emd21,tx21,rx21,threshold=100)
# mask10 = eval_cmap(emd10,tx10,rx10,threshold=600)



































#
