
import os
import time
import numpy as np
import shutil
from pathlib import Path
# from igor2 import packed
import platform
from collections import defaultdict
import tifffile as tf
import re
from matplotlib import animation
from matplotlib import colors

# TODO: igor2 only open 'simple' waves

def subplots(arrs=[], title=''):

    fig, axs = plt.subplots(2, 2)
    fig.suptitle(title)

    # create a single norm to be shared across all images
    # norm = colors.Normalize(vmin=np.min(arrs), vmax=np.max(arrs))

    images = []
    for ax, data in zip(axs.flat, arrs):
        # images.append(ax.imshow(data, norm=norm))
        images.append(ax.imshow(data))
        
    # fig.colorbar(images[0], ax=axs, orientation='horizontal', fraction=.1)
    plt.show()


# just in case, to define colors manually
palette = np.array([[255, 255, 255],   # 0:white
                    [  0, 255,   0],   # 1:green
                    [  0,   0, 255],   # 2:blue
                    [255,   0,   0],   # 3:red
                    [255, 255,   0],   # 4:yellow
                    [255, 128,   0],   # 5:orange
                    [255, 153, 255],   # 6:pink
                    [160,  32, 240],   # 7:purple
                    [128, 128, 128],   # 8:gray
                    [  0,   0,   0]])  # 9:black

# plot animation
def animplot(iims, rows=0, cols=0, step=100, color='gray', title='', mask=[], from_palette=False):
    # make list for subplots
    if not isinstance(iims, list):
        iims = [iims]
    # number of frames
    nf = iims[0].shape[0]
    # if only one, make copy & process later
    if len(iims) == 1:
        cp = iims[0].copy()
        copy_index = 1
        iims.append(cp)
    # mk subplots
    if rows + cols == 0:
        rows = 1 if len(iims) <= 2 else 2
        cols = 2 if len(iims) <= 2 else int(len(iims)/2) + len(iims)%2
    fig, axs = plt.subplots(rows,cols, figsize=(10,5))
    # basic vars
    ti = 0
    ims = []
    fig.suptitle(title)
    for ei,ax in enumerate(axs.flat):
        im = ax.imshow(iims[ei][ti], cmap=color, aspect='auto', animated=True)
        # im = ax.imshow(palette[iims[ei][ti].astype(int)])
        ims.append(im)
    def update_fig(ti):
        ti = (ti+1)%nf
        fig.suptitle(f'{title} {ti+1}/{nf}')
        for ui,ax in enumerate(axs.flat):
            # do stuff
            if len(mask) > 0:
                iims[copy_index][ti] = iims[copy_index][ti] * mask
            # import pdb; pdb.set_trace()
            if from_palette:
                ax.imshow(palette[iims.astype(int)])
                ims[ui].set_array(palette[iims[ui][ti].astype(int)])
            else:
                ax.imshow(iims[ui][ti].astype(int))
                ims[ui].set_array(iims[ui][ti])
        return [im for im in ims]
    anim = animation.FuncAnimation(fig,update_fig,interval=step,blit=False,repeat=True,cache_frame_data=False)
    plt.show()
    plt.close()
    # return anim

# search for file with some ext or tag in the same folder as another file
# as_list returns data as list, be it 0, 1 or many
# tag assumes separation usgin underscores
def search_in_filedir(fpath,ext='',tag='',as_list=False):
    sep = '\\' if platform.system() == 'Windows' else '/'
    fdir = sep.join(fpath.split(sep)[:-1])
    files = [os.path.join(fdir,x) for x in os.listdir(fdir) if x.endswith(str(ext))]
    if tag:
        tag_files = []
        for file in files:
            if tag in file.split('_'):
                tag_files.append(file)
        files = tag_files
    if as_list:
        return files
    files = files[0] if len(files) > 0 else ''
    return files

# save in the same folder of fpath
def mk_savepath(fpath,ext='',tag=''):
    sep = '\\' if platform.system() == 'Windows' else '/'
    fdir = sep.join(fpath.split(sep)[:-1])
    name, oext = fpath.split(sep)[-1].split('.')
    # if different extension
    ext = ext if ext else oext
    # if extra tag
    tag = f'_{tag}' if tag else ''
    # mk savepath
    fname = f'{name}{tag}.{ext}'
    savepath = os.path.join(fdir,fname)
    # to avoid overwrite or crashing
    if os.path.isfile(savepath):
        now = time.time()
        sname, sext = savepath.split('.')
        savepath = f'{sname}_{now}.{sext}'
    return savepath

# makes a dictionary with info from every slice about some tag
def get_medata_from_tif(tif_file_path,tag='ImageDescription'):
    tif = tf.TiffFile(tif_file_path)
    # print for info
    print(f'currently using tag={tag}. Other tags are:')
    for tx in tif.pages[0].tags.values():
        print(tx.name)
    # there are different tags, I'm only getting this for now
    raw_info = [page.tags[tag].value for page in tif.pages]
    # parse
    tag_info = defaultdict(list)
    for page in raw_info:
        for x in page.split('\r'):
            key,value = x.split('=')
            tag_info[key] += value
    return tag_info

# converts list of (start, end) to indices for np arrays
def mk_np_indexes(indexes):
    return np.concatenate([np.arange(a,b) for a,b in indexes])

# just print some wave data
def print_wave_data(wave):
    print('\nwave header')
    for k,v in wave['wave_header']:
        print(f'{k}: {v}')
    print('\nnote:')
    for x in wave['note'].decode(errors='replace').split('\r'):
        print(x)

# just read and returns data points from the .itx file
def read_itx(fpath_itx):
    if os.path.isfile(fpath_itx) and fpath_itx.endswith('itx'):
        p = Path(fpath_itx)
        # replaces invalid chars with unicode repl char: '?'
        # the 'ignore' option just removes them, but this safeguards structure
        itx_data = p.read_text(errors='replace')
    else:
        raise '\nit isn\'t an .itx file\n'
    li = itx_data.split(',')
    pxs = li[0].split('\n')
    data_points = np.array([float(px[2:]) for px in pxs if px.startswith('\t')])
    return data_points

# check path for loading (dir or file)
def check_file_dir(path):
    if os.path.isfile(path):
        return path
    if os.path.isfile(os.path.join(os.getcwd(),path)):
        return os.path.join(os.getcwd(),path)
    if os.path.isidr(path):
        return path

# look for dir in folders (going up only)
def dir_upsearch(dirname, filename=None, verbose=False):
    for i in range(5):
        cdir = os.path.abspath('../'*i)
        if verbose:
            print(f'looking in: {cdir}')
        if dirname in os.listdir(cdir):
            fpath = os.path.join(cdir,dirname)
            print(os.listdir(fpath))
            if filename and filename in os.listdir(fpath):
                if verbose:
                    print(os.listdir())
                fpath = os.path.join(fpath,filename)
            if verbose:
                print(fpath)
            return fpath
    return os.getcwd()

# to convert a string of items into a list of arguments
def string_as_list(string):
    # check if commas + spaces
    if ', ' in string:
        string.replace(',',' ')
    return string.split(',')
    # check if sepparated only by commas (no spaces)
    if ',' in string:
        return string.split(',')
    # else (as it is)
    return [string]
    

# simple de-interleave
def deinterleave(stack):
    ch1 = stack[0::2]
    ch2 = stack[1::2]
    return ch1,ch2

# raw way to look inside methods of an object
# in_name assumes names separated by '_'
def inspect_methods(object, in_name='',startswith='',endswith=''):
    # filter some methods (optional, otherwise it will include all)
    mxs = []
    for method in dir(object):
        if method.startswith(str(startswith)):
            mxs.append(method)
        elif method.endswith(str(endswith)):
            mxs.append(method)
        elif re.search(str(in_name),method):
            mxs.append(method)
    # check if possible
    for mx in mxs:
        print()
        print(mx)
        try:
            x = getattr(object,mx)
            print(f'{mx}: {x}')
        except:
            print(x)
            print('prob require args')

# for windows temp handling issue
def rmtree_retry(path, tries=30, delay=0.1):
    for i in range(tries):
        try:
            shutil.rmtree(path)
            return
        except PermissionError:
            time.sleep(delay)
    # last try (raise if still locked)
    shutil.rmtree(path)


import matplotlib.pyplot as plt
def animated_imshow(arr, title=''):
    # First set up the figure, the axis, and the plot element we want to animate
    fig = plt.figure()
    ax = plt.axes(xlim=(0, 10), ylim=(0, 10))
    im=plt.imshow(arr[0])

    # initialization function: plot the background of each frame
    def init():
        im.set_data(np.random.random((5,5)))
    return im

    # animation function.  This is called sequentially
    def animate(i):
        a=im.get_array()
        a=a*np.exp(-0.001*i)    # exponential decay of the values
        im.set_array(a)
        return im
























#
