#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import numpy as np
from scipy.ndimage import convolve
from tqdm import tqdm


def gauss1d(size,sigma=0.8):
    # make the gaussian
    w = np.arange(-(size//2), size//2+1)
    gw = np.exp(-(w**2) / (2*sigma**2))
    # normalize
    gw /= gw.sum()
    return gw

# make kernel_2d

def mk_kernel3d(arr, kdt=3, kdy=1, kdx=3, sigma=0.8):
    gt = gauss1d(kdt, sigma=sigma)
    gy = gauss1d(kdy, sigma=sigma)
    gx = gauss1d(kdx, sigma=sigma)
    kernel = gt[:,None,None] * gy[None,:,None] * gx[None,None,:]
    return kernel

# import pdb; pdb.set_trace()
                
def conv3d(arr, kdt=3, kdy=1, kdx=3, sigma=0.8):
    cxmap = np.zeros((arr.shape))
    kernel3d = mk_kernel3d(arr, kdt=kdt, kdy=kdy, kdx=kdx, sigma=sigma)
    for dt in tqdm(range(arr.shape[0]-kdt)):
        for dy in range(arr.shape[1]-kdy):
            for dx in range(arr.shape[2]-kdx):
                vx = arr[dt:dt+kdt,dy:dy+kdy,dx:dx+kdx]
                cxmap[dt,dy,dx] = (vx * kernel3d).sum()
    return cxmap

# 0.5: light smoothing
# 0.7 - 0.9: denoising
# 1.2: box filter
def conv3d_scipy(arr, kdt=3, kdy=1, kdx=3, sigma=0.8):
    kernel = mk_kernel3d(arr, kdt=kdt, kdy=kdy, kdx=kdx, sigma=sigma)
    filtered_movie = convolve(arr, kernel, mode='reflect')
    return filtered_movie