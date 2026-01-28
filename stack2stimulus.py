
import numpy as np
import tifffile as tf
from auxs import get_medata_from_tif, deinterleave, mk_savepath
import matplotlib.pyplot as plt
from igorwriter import IgorWave

# ideally in each exp folder, you'd like to have at least 3 files:
# raw tif, ch2 tif/itx/txt, reg tif

# convert tensor from ch2 into a 1d array rep. the stimulus
# python implemenation of Jamie's code for Igor
def ch2stimulus(fpath):
    # simple check for reg
    if not 'reg' in fpath.split('_'):
        # assuming not de-interleaved:
        stack = tf.imread(fpath)
        ch1,ch2 = deinterleave(stack)
    else:
        ch2 = tf.imread(fpath)
    # get image description data from tif file
    # msPerLine doesn't change with processing
    chdata = get_medata_from_tif(fpath)
    # get msPerline
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
        raise Exception('\nincorrect kind of file? dims of stack != 3\n')
    # z:t:1200, y:rows:50, x:cols:120
    z,y,x = ch2.shape
    # sum everything all columns into one: 1200 x 50
    zy = ch2.sum(axis=2)
    # 50 scan lines (temporal bands)
    # each linescan is a sample, so total samples are 60,000 (50x1200)
    yz = zy.T
    # according to chat-gpt igor follows Fortran order (!= np.flatten())
    yz_1d = yz.reshape(y * z, order='F')
    # jose's scaling for intensity
    yz_1d = yz_1d/1000000
    # dts in seconds per line (for plotting only)
    tx = np.arange(yz_1d.size) * dt
    # plot & save
    png_savepath = mk_savepath(fpath,tag='timewave',ext='png')
    plt.plot(tx, yz_1d)
    plt.savefig(png_savepath)
    plt.show(block=False)
    plt.pause(3)
    plt.close()
    # save to folder as igor itx
    itx_savepath = mk_savepath(fpath,tag='timewave',ext='itx')
    wave = IgorWave(yz_1d, name='stim_timewave')
    wave.save_itx(itx_savepath)
    return yz_1d
