

# first images have to be de-interleaved and registered
# prob using Igor, which works better than faster than fiji
# i could also use caiman, but i'd have to make in a conda env...

import os
import platform
import tempfile
from auxs import *
import tifffile as tf
import numpy as np
import caiman as cm
from caiman.motion_correction import MotionCorrect
import matplotlib.pyplot as plt
import gc

# load movie
if platform.system() == "Darwin":
    fpath = "/Users/f/Dropbox/_r66y/r66xe/2p_data/step_a1.tif"
elif platform.system() == "Windows":
    fpath = 'C:/Users/Fernando/zf/data/glu_a1/steps_pre_AF10_a1001_test.tif'

if not os.path.isfile(fpath):
    exp_name = fpath.split('/')[-1]
    fpath = dir_upsearch(dirname='data',filename=exp_name,verbose=True)
if not os.path.isfile(fpath):
    fpath = file_menu(path=fpath, file_ext=['tif','tiff'])

stack = tf.imread(fpath)

# de-interleave
response, ch2 = deinterleave(stack)

# convert to 32 bit
# response = response.astype(np.float32, copy=False)
# actually, igor inly do 16 bit, so i'm leaving it this way

# registration (rigid body)
def caiman_reg(stack):

    td = tempfile.mkdtemp()

    try:
        temp_path = os.path.join(td, "temp.tif")
        tf.imwrite(temp_path, stack)

        mc = MotionCorrect(
            temp_path,
            dview=None,
            # pw : piecewise (only translation)
            # if False : global rigid motion
            pw_rigid=False,
            max_shifts=(10, 10),
            shifts_opencv=True,
            nonneg_movie=True,
            border_nan="copy",
            # ignored for pure rigid:
            # strides=strides,
            # overlaps=overlaps,
        )

        mc.motion_correct(save_movie=True)

        # movie from temp to mmap - float32 (T,Y,X)
        reg = cm.load(mc.mmap_file)
        reg_np = np.asarray(reg)

        # windows have problems with open temps
        if platform.system() == 'Windows':
            try:
                reg.close()
            except:
                pass

            del reg
            del mc
            gc.collect()

    finally:
        rmtree_retry(td)

    return reg_np

# rx = caiman_reg(response)
# rx_clean = np.nan_to_num(rx, nan=0.0)


##### print/plot some info

print("RAW dtype/range:", response.dtype, response.min(), response.max())
print("REG dtype/range:", rx.dtype, np.nanmin(rx), np.nanmax(rx))

raw_mean = response.mean(axis=0)
reg_mean = rx.mean(axis=0)
vmin, vmax = np.percentile(raw_mean, [1, 99])  # use RAW limits
plt.figure(); plt.imshow(raw_mean, cmap="gray", vmin=vmin, vmax=vmax); plt.title("raw mean"); plt.axis("off")
plt.figure(); plt.imshow(reg_mean, cmap="gray", vmin=vmin, vmax=vmax); plt.title("reg mean (same scale)"); plt.axis("off")
plt.show()

# stick with 16-bit
# tf.imwrite("test.tif", rx.astype(np.float32))

def to_uint16(movie_f, lo=None, hi=None):
    if lo is None or hi is None:
        lo, hi = np.percentile(movie_f, [0.5, 99.5])  # robust display range
    m = np.clip(movie_f, lo, hi)
    m = (m - lo) / (hi - lo + 1e-12)
    return (m * 65535).round().astype(np.uint16), (lo, hi)

# rx_u16, (lo, hi) = to_uint16(rx)

fname = fpath.split('/')[-1].split('.')[0]
tf.imwrite(f'{fname}_caimanreg', rx)
print("saved with lo/hi:", lo, hi)









#
