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
    if normalize:
        fig.colorbar(images[0], ax=axs, orientation='vertical', fraction=.1)
    plt.show()



# plot animated imshow
def tensor_animation(iims, rows=0, cols=0, step=100, color='gray', title='', mask=[], from_palette=False):
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