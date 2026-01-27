
import numpy as np
import tifffile as tf
from auxs import get_medata_from_tif, deinterleave
import matplotlib.pyplot as plt

# python implemenation of Jamie's code for Igor
fpath = 'C:/Users/Fernando/zf/data/ca_a1/step_HUC_a1.tif'

def get_image_description(fpath):
    with th.TiffFile(fpath) as tif:
        return tif.pages[0].tags['ImageDescription'].value

def ch2stimulus(fpath):
    # assuming not de-interleaved:
    stack = tf.imread(fpath)
    ch1,ch2 = deinterleave(stack)

    # get image description data from tif file
    chdata = get_medata_from_tif(fpath)
    # get msPerline & fillFraction
    ms_pl = np.asarray(chdata['state.acq.msPerLine']).astype(float)
    # check if the same for every slice
    if np.all(ms_pl == ms_pl[0]):
        ms_pl = ms_pl[0]
    else:
        raise 'acquisition rate isn\'t fixed'
    # miliseconds to seconds per line
    dt = ms_pl/1000

    # tensor processing
    if len(ch2.shape) != 3:
        raise 'incorrect kind of file'
    # z:t:1200, y:rows:50, x:cols:120
    z,y,x = ch2.shape
    # sum everything all columns into one: 1200 x 50
    zy = ch2.sum(axis=2)
    # 50 scan lines (temporal bands)
    # each linescan is a sample, so total samples are 60,000 (50x1200)
    yz = zy.T
    # according to chat-gpt igor follows Fortran order (!= np.flatten())
    yz_1d = yz.reshape(y * z, order='F')
    # jose's normalization for intensity
    yz_1d = yz_1d/1000000
    # dts in seconds per line (for plotting only)
    tx = np.arange(yz_1d.size) * dt
    plt.plot(tx, yz_1d)
    plt.show()
    return yz_1d, secs
