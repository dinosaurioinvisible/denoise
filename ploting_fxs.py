# -*- coding: utf-8 -*-
"""
Created on Wed Feb 11 10:15:36 2026

@author: Fernando
"""

import numpy as np
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


# TODO: flexible
# simple fx to arrange 4 subplots 
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
    
    
    
    
    
    
    
    
    
    
    
    









































#