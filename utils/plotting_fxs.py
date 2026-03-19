# -*- coding: utf-8 -*-
"""
Created on Wed Feb 11 10:15:36 2026

@author: Fernando
"""

import numpy as np
from numpy.ma import masked_array
import matplotlib.pyplot as plt
from matplotlib import animation
from matplotlib import colors
from utils.auxs import datapoints_in_seconds


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


def plot_in_seconds(arr,freq,title=''):
    nframes = arr.size
    x = np.linspace(0,nframes/freq,nframes)
    plt.plot(x,arr)
    plt.title(title)
    plt.show()


def mk_raster_plot(arr, locs, stimulus=None, title='', mk_cbar=True, in_seconds=False):
    raster = np.zeros((locs.shape[0],arr.shape[0]))
    for ei,(row,col) in enumerate(locs):
        if in_seconds:
            raster[ei] = arr[:,row,col]
        else:
            raster[ei] = arr[:,row,col]
    if isinstance(stimulus,np.ndarray):
        f, (a0,a1) = plt.subplots(2,1, gridspec_kw={'height_ratios': [1,7]})
        a0.plot(stimulus)
        a0.set_xlim(xmin=0, xmax=stimulus.size)
        a0.set_xticks([])
        a0.set_yticks([])
        im = a1.imshow(raster, aspect='auto')
        a1.set_ylim(ymax=0, ymin=locs.shape[0]-1)
        a1.set_xticks(np.arange(0,stimulus.size+1,150))
        a1.set_yticks(np.arange(0,locs.shape[0],5))
        if mk_cbar:
            plt.colorbar(im, orientation='horizontal')
        plt.suptitle(title)
        plt.show()
        plt.tight_layout()
    else:
        simple_plot(raster, mk_cbar=mk_cbar, title=title, aspect='auto')
    return raster


def simple_plot(arr, arr2=None, title='', mk_cbar=False, size=[], aspect='equal'):
    if isinstance(size,int):
        plt.figure(figsize=(size,size))
    elif len(size)==2:
        ysize, xsize = size
        plt.figure(figsize=(ysize,xsize))
    else:
        pass
    if isinstance(arr2,np.ndarray):
        if mk_cbar:
            im = plt.plot(arr,arr2)
            plt.colorbar(im, orientation='horizontal')
        else:
            plt.plot(arr,arr2)
    elif len(arr.shape) == 1:
        if mk_cbar:
            im = plt.plot(arr)
            plt.colorbar(im, orientation='horizontal')
        else:
            plt.plot(arr)
    elif len(arr.shape) == 2:
        if mk_cbar:
            im = plt.imshow(arr)
            plt.colorbar(im, orientation='horizontal')
        else:
            plt.imshow(arr)
    else:
        print('\ncouldn\'t interpret data as plot')
        return
    plt.gca().set_aspect(aspect)
    plt.title(title)
    plt.show()


# for plotting specific sparse points on top a background image
# uses 2 colormaps
def overlaying_imshows(background,mask1,mask2=[],title='',xlabel='',ylabel='',cbar2_label=''):
    # set backgorund
    fig,ax = plt.subplots()
    background_im = ax.imshow(background, cmap='viridis', alpha=0.95)
    cb1 = plt.colorbar(background_im, shrink=0.5)
    cb1.set_label('background')
    # np mask for plotting
    mask1 /= mask1.max()
    mk1 = masked_array(mask1,mask1<=0)
    pxs1 = ax.imshow(mk1, cmap='cool')
    # mask2
    if len(mask2) > 0:
        mask2 /= mask2.max()
        mk2 = masked_array(mask2,mask2<=0)
        pxs2 = ax.imshow(mk2, cmap='cool')
    # mask cbar
    cb2 = plt.colorbar(pxs1, shrink=0.5)
    cb2.set_label(cbar2_label)
    # labeling
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    plt.title(title)
    plt.show()


# simple fx to arrange plot/subplots 
def mk_plots(iims=[], rows=0, cols=0, title='', subtitles=[], normalize=False, from_palette=False):
    # if one image
    if not isinstance(iims, list):
        plt.title(title)
        if len(iims.shape) == 2:
            plt.imshow(iims)
        else:
            plt.plot(iims)
        plt.title(title)
        plt.show()
        return
    # mk subplots
    if rows + cols == 0:
        rows = 1 if len(iims) <= 2 else 2
        cols = 2 if len(iims) <= 2 else int(len(iims)/2) + len(iims)%2
    fig, axs = plt.subplots(rows,cols, figsize=(10,5))
    fig.suptitle(title)
    # create a single norm to be shared across all images
    if normalize:
        images = []
        norm = colors.Normalize(vmin=np.min(iims), vmax=np.max(iims))
    for ei,(ax,image) in enumerate(zip(axs.flat, iims)):
        if len(subtitles) == len(iims):
            ax.set_title(subtitles[ei])
        # for custom cases
        if from_palette:
            ax.imshow(palette[iims.astype(int)])
        if normalize:
            if len(image.shape) == 2:
                images.append(ax.imshow(image, norm=norm))
            else:
                images.append(ax.plot(image, norm=norm))
        else:
            if len(image.shape) == 2:
                ax.imshow(image)
            else:
                ax.plot(image)
                ax.set_xlim(xmin=0,xmax=image.size)
                if ei != len(iims)-1:
                    ax.set_xticks([])
    if normalize:
        fig.colorbar(images[0], ax=axs, orientation='horizontal', fraction=.1)
    plt.tight_layout()
    plt.show()



# plot animated imshow
def tensor_animation_subplots(iims, rows=0, cols=0, step=100, color='gray', title='', mask=[], 
                     from_palette=False):
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
    else:
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
        ims.append(im)
        if from_palette:
            im = ax.imshow(palette[iims[ei][ti].astype(int)])
    def update_fig(ti):
        ti = (ti+1)%nf
        fig.suptitle(f'{title} {ti+1}/{nf}')
        for ui,ax in enumerate(axs.flat):
            # do stuff
            if len(mask) > 0:
                iims[copy_index][ti] = iims[copy_index][ti] * mask
            # import pdb; pdb.set_trace()
            if from_palette:
                ims[ui].set_array(palette[iims[ui][ti]])
            else:
                ims[ui].set_array(iims[ui][ti])
        return [im for im in ims]
    anim = animation.FuncAnimation(fig, update_fig,
                                   interval=step,blit=False,
                                   repeat=True,
                                   cache_frame_data=False)
    plt.show()
    plt.close()
    # return anim

def tensor_animation(arr, step=10, color='gray', title='', mask='',
                     squared=True, repeat=True, blit=False):
    # import pdb; pdb.set_trace()
    if not isinstance(arr,np.ndarray) or len(arr.shape) != 3:
        raise Exception('\nnon an array or invalid dimensions')
    ti = 0
    nf = arr.shape[0]
    aspect = 'auto' if squared == True else 'equal'
    fig,ax = plt.subplots()
    im = ax.imshow(arr[ti], cmap=color, animated=True, aspect=aspect)
    
    def update_fig(ti):
        ti = (ti+1)%nf
        fig.suptitle(f'{title} {ti+1}/{nf}')
        im.set_data(arr[ti])
        return [im]
    anim = animation.FuncAnimation(fig, update_fig,
                                   interval=step,
                                   blit=blit,
                                   repeat=repeat)
    plt.show()
    plt.close()
    

def tensor_animation_pausable(arr, step=10, color='gray', title='', mask='',
                     squared=True, repeat=True, blit=True):
    if not isinstance(arr,np.ndarray) or len(arr.shape) != 3:
        raise Exception('\nnon an array or invalid dimensions')
    
    nf = arr.shape[0]
    aspect = 'auto' if squared == True else 'equal'
    fig,ax = plt.subplots()
    fig.suptitle("{}".format(title),ha="center",va="center")
    time = fig.text(0.5,0.95,"",ha="center",va="center")
    im = ax.imshow(arr[0], cmap=color, animated=True, aspect=aspect)

    # to pause the animation and check data
    anim_running = True
    def onClick(event):
        nonlocal anim_running
        if anim_running:
            anim.event_source.stop()
            anim_running = False
        else:
            anim.event_source.start()
            anim_running = True
        movie = arr.copy()
        print('\n\nvars: movie =  array\n')
        import pdb; pdb.set_trace()
    
    def init():
        return True
    
    def animate(i):
        time.set_text("time={}/{}".format(i,nf))
        im.set_data(arr[i])
        return [im]
    
    fig.canvas.mpl_connect('button_press_event', onClick)
    anim = animation.FuncAnimation(fig, animate,
                                   frames=nf,
                                   interval=step,
                                   blit=blit,
                                   repeat=repeat)
    plt.show()
    

    
    
    
    
    
    
    
    









































#