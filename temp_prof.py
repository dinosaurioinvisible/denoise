
import os
from auxs import *
import tifffile as tf
import numpy as np
import matplotlib.pyplot as plt
from matplotlib import colors
import platform
import caiman as cm
from caiman.motion_correction import MotionCorrect
import seaborn as sns
from scipy.stats import kurtosis
from tqdm import tqdm
# from loading import load_pxp

# # full path to file
# igor_exp_path = 'C:\\Users\\Fernando\\zf\\data\\glu_a1\\caiman_igor_reg_comparison_glu.pxp'
# response, response_reg, stimulus = load_pxp(igor_exp_path)

response = tf.imread('C:\\Users\\Fernando\\zf\\data\\glu_a1\\steps_pre_AF10_a1001.tif')
response_reg = tf.imread('C:\\Users\\Fernando\\zf\\data\\glu_a1\\steps_pre_AF10_a1001_Ch1_reg.tif')
stimulus = read_itx('C:\\Users\\Fernando\\zf\\data\\glu_a1\\steps_timewave.itx')

# match response & stimulus data
# get steps
print(f'stimulus points: {len(stimulus)}')
steps = get_steps_vals(stimulus,delta=0.1)

# get response freq
rx_freq = stimulus.shape[0]/response.shape[0]
print(f'\nresponse datapoints = {response.shape[0]}')
print(f'stimulus points = {stimulus.shape[0]}')
print(f'1 response every: {rx_freq} stimulus points')

# convert step indexes from stimulus > response arrays
steps[:,:2] = (steps[:,:2]/rx_freq).astype(int)
print('\nsteps:\n')
print(steps)

# assuming stimulus values: 0:low, 1:rest, 2:high
low = steps2indexes(steps,0)
high = steps2indexes(steps,2)
# separate base from in-between resting periods
# base = steps2indexes(steps,1,base=True)
# rest = steps2indexes(steps,1)[1:-1]
# TODO: rest/base comparison
# doesn't seem to be necessary?
rest = steps2indexes(steps,1)

# check profiles
# TODO: caiman comparison
# ribase = response_reg[base]
# rcbase = response_caimanreg[base]
rirest = response_reg[rest]
# rcrest = response_caimanreg[rest]
rilow = response_reg[low]
# rclow = response_caimanreg[low]
rihigh = response_reg[high]
# rchigh = response_caimanreg[high]

# print some examples
def compare_pixels(arr1,arr2,arr3,row,col,title=''):
    r1 = arr1[:,row,col]
    r2 = arr2[:,row,col]
    r3 = arr3[:,row,col]
    # plt.plot(r1)
    # plt.plot(r2)
    sns.distplot(r1)
    sns.distplot(r2)
    sns.distplot(r3)
    if title:
        plt.title(title)
    plt.show()

# print some exaples
# for _ in range(10):
#     row = np.random.randint(0,50)
#     col = np.random.randint(0,128)
#     compare_pixels(rirest,rilow,rihigh,row,col,title=f'row={row}, col={col}')

# search for pixels with non-gaussian behavior
# dict for storing low, rest, high intensity cases
# rmap_mean =
rmap_mad = np.zeros((5,50,128))
rmap_kur = np.zeros((6,50,128))
for row in tqdm(range(50)):
    for col in range(128):
        # compare distributions
        dl = rilow[:,row,col]
        dr = rirest[:,row,col]
        dh = rihigh[:,row,col]
        # mad val - MAD = median * (|x - median(x)|)
        madl = np.median(np.abs(dl - np.median(dl)))
        madr = np.median(np.abs(dr - np.median(dr)))
        madh = np.median(np.abs(dh - np.median(dh)))
        # mad ratio - for a gausian dist: SD ~ mad * 1.4826 => SD/MAD = 1.4826
        madr_l = (np.std(dl) / madl) /1.4826
        madr_r = (np.std(dr) / madr) /1.4826
        madr_h = (np.std(dh) / madh) /1.4826
        # if fisher=False => Pearson's (raw) & kurtosis of mean of normal dist = 3, instead of 0
        kur_l = kurtosis(dl, axis=0, fisher=True)
        kur_r = kurtosis(dr, axis=0, fisher=True)
        kur_h = kurtosis(dh, axis=0, fisher=True)

        # if abs(kur_l) >= 10 or abs(kur_h) >= 10 or madr_l >= 1.5 or madr_h >= 1.5:
        if madr_l > 1.5 or madr_h > 1.5:
            # use base as contrast (should be normal)
            compare_pixels(rilow,rihigh,rirest,row,col,title=f'px=({row},{col}) - mad={madr_l:.2f},{madr_r:.2f},{madr_h:.2f} - kurtosis={kur_l:.2f},{kur_r:.2f},{kur_h:.2f}')
            rmap_mad[:,row,col] = 1

        rmap_mad[0][row][col] = madr_l
        rmap_mad[1][row][col] = madr_r
        rmap_mad[2][row][col] = madr_h
        rmap_kur[0][row][col] = kur_l
        rmap_kur[1][row][col] = kur_r
        rmap_kur[2][row][col] = kur_h


# # rmap MAD relations
rmap_mad[3] = rmap_mad[0]/rmap_mad[1]
rmap_mad[4] = rmap_mad[2]/rmap_mad[1]
# rmap[5] =
# rmap[6] = rilow.mean(axis=0)
# rmap[7] = rirest.mean(axis=0)
# rmap[8] = rihigh.mean(axis=0)

for i in range(rmap_mad.shape[0]):
    plt.imshow(rmap_mad[i])
    # plt.colorbar(rmap_mad.shape[0])
    plt.show()



# fig,axs = plt.subplot(3,3)
# fig.suptitle('MAD plots')
# vmin = np.min(madr_l.min(),madr_r.min(),madr_h.min())
# vmax = np.max(madr_l.max(),madr_r.max(),madr_h.max())
# color_norm = colors.Normalize(vmin=vmin, vmax=vmax)
# images = []
# for ax,rmap in zip(axs.flat, rmap_mad):
#     images.append(ax.imshow(rmap, norm=color_norm))
# axs[0].set_title()
# axs[1].set_title()
# axs[2].set_title()
# axs[3].set_title()
# axs[4].set_title()
# axs[5].set_title()
# fig.colorbar(images[0], ax=axs, orientation='vertical', fraction=.1)
# plt.show()


from scipy.stats import kstest

def compare_ks(d1,d2,rows=50,cols=128):
    cmap = np.zeros((50,128))
    for row in tqdm(range(rows)):
        for col in range(cols):
            x = kstest(d1[:,row,col],d2[:,row,col])
            cmap[row][col] = x.statistic
    plt.imshow(cmap)





















#
