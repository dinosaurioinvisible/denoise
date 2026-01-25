
import os
from auxs import *
import tifffile as tf
import numpy as np
import matplotlib.pyplot as plt
import platform
import caiman as cm
from caiman.motion_correction import MotionCorrect
import seaborn as sns
from scipy.stats import kurtosis

# path to folder
if platform.system() == "Darwin":
    exp_path = "/Users/f/Dropbox/_r66y/r66xe/2p_data/ca_a1"
elif platform.system() == "Windows":
    exp_path = 'C:/Users/Fernando/zf/data/ca_a1'

# try to load from igor experiment
fpath = None
if os.path.isdir(exp_path):
    for f in os.listdir(exp_path):
        if f.endswith('.pxp'):
            fpath = os.path.join(exp_path,f)
    if fpath:
        rx_wave, reg_wave, sti_wave = load_waves_from_igor_exp(fpath)
        fname = fpath.split('/')[-1].split('.')[0]
        # transpose axes: [time][y][x] - i like [t][x][y] but it's conv...
        response = rx_wave['wData'].T
        response_reg = reg_wave['wData'].T
        stimulus = sti_wave['wData']
        stimulus = stimulus/10**6 if stimulus.mean() > 100 else stimulus
else:
    # define stack/movie path
    if platform.system() == "Darwin":
        fpath = "/Users/f/Dropbox/_r66y/r66xe/2p_data/ca_a1/step_HUC_a1.tif"
    elif platform.system() == "Windows":
        fpath = 'C:/Users/Fernando/zf/data/ca_a1/step_HUC_a1.tif'
    # if not, look for file in parent folders
    if not os.path.isfile(fpath):
        fpath = dir_upsearch(dirname='ca_a1',filename=exp_name,verbose=True)
    # if not, load the menu to load whatever pxp or tif
    if not os.path.isfile(fpath):
        fpath = file_menu(path=fpath, file_ext=['tif','tiff','pxp'])
    # load stimulus data (itx file from channel 2)
    fpath_itx = fpath.split('/')[0]+'timewave.itx'
    if not os.path.isfile(fpath_itx):
        fpath_itx = file_menu(path=fpath, file_ext='')
    stimulus = read_itx(fpath_itx)
    # names
    exp_path = fpath.split('.')[0]
    fname = exp_path.split('/')[-1].split('.')[0]
    # actually load
    stack = tf.imread(fpath)
    # de-interleave
    response, ch2 = deinterleave(stack)

# load or register with caiman
fpath_caiman = f'{exp_path}/{fname}_caimanreg.tif'
if not os.path.isfile(fpath_caiman):
    max_shifts = (6, 6)  # maximum allowed rigid shift in pixels (view the movie to get a sense of motion)
    # strides =  (48, 48)  # create a new patch every x pixels for pw-rigid correction
    # overlaps = (24, 24)  # overlap between patches (size of patch strides+overlaps) / pw
    max_deviation_rigid = 3   # maximum deviation allowed for patch with respect to rigid shifts
    pw_rigid = False # flag for performing rigid or piecewise rigid motion correction
    shifts_opencv = True  # flag for correcting motion using bicubic interpolation (otherwise FFT interpolation is used)
    border_nan = 'copy'  # replicate values along the boundary (if True, fill in with NaN)

    # create a motion correction object
    tif_fpath = f'{os.path.join(exp_path,fname)}_de-int.tif'
    if not os.path.isfile(tif_fpath):
        print(f'\ncouldn\'t find {tif_fpath}')
        tif_fpath = file_menu(exp_path)
    mc = MotionCorrect(tif_fpath, dview=None, max_shifts=max_shifts,
                      # strides=strides, overlaps=overlaps,
                      max_deviation_rigid=max_deviation_rigid,
                      shifts_opencv=shifts_opencv, nonneg_movie=True,
                      border_nan=border_nan)

    mc.motion_correct(save_movie=True)    
    m_rig = cm.load(mc.mmap_file)
    
    # save
    tf.imwrite(f'{fpath_caiman}', m_rig)
    print(f'\nsaved at : {fpath_caiman} \n')
    
response_caimanreg = tf.imread(fpath_caiman)

# match response & stimulus data 

# get steps
print(f'stimulus points: {len(stimulus)}')
steps = get_steps_vals(stimulus,delta=0.5)

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
rmap = np.zeros((3,50,128))
for row in range(30,33):
    for col in range(128):
        # compare distributions
        dl = rilow[:,row,col]
        dr = rirest[:,row,col]
        dh = rihigh[:,row,col]
        # mad val - MAD = median * (|x - median(x)|)
        madl = np.median(np.abs(np.std(dl) - np.median(dl)))
        madr = np.median(np.abs(np.std(dr) - np.median(dr)))
        madh = np.median(np.abs(np.std(dh) - np.median(dh)))
        # mad ratio - for a gausian dist SD ~ mad * 1.4826 (i.e. how far from gausian)
        madr_l = np.std(dl) / (1.4826 * madl)
        madr_r = np.std(dr) / (1.4826 * madr)
        madr_h = np.std(dh) / (1.4826 * madh)
        # if fisher=False => Pearson's (raw) & kurtosis of mean of normal dist = 3, instead of 0
        kur_l = kurtosis(dl, axis=0, fisher=True)
        kur_r = kurtosis(dr, axis=0, fisher=True)
        kur_h = kurtosis(dh, axis=0, fisher=True)
        if abs(kur_l) >= 1.5 or abs(kur_h) >= 1.5 or madr_l >= 1.5 or madr_h >= 1.5:
            # use base as contrast (should be normal)
            compare_pixels(rilow,rihigh,rirest,row,col,title=f'px=({row},{col}) - mad={madr_l:.2f},{madr_r:.2f},{madr_h:.2f} - kurtosis={kur_l:.2f},{kur_r:.2f},{kur_h:.2f}')
            rmap[:,row,col] = 1



































#
