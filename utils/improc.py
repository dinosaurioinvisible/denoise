#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import numpy as np
from scipy.ndimage import convolve
from tqdm import tqdm


def gauss1d(size, sigma=0):
    # make the gaussian 
    r = size//2
    w = np.arange(-r, r+1)
    # default sigma = radius
    sigma = size/2 if sigma == 0 else sigma
    gw = np.exp(-(w**2) / (2*sigma**2))
    # normalize
    gw /= gw.sum()
    return gw

def gauss2d(size, sigma=0):
    # make the 1d gaussian
    r = size//2
    gx = np.arange(-r, r+1)
    # default sigma: diameter / 2.83 
    # from max 2d response: r = sqrt(2) * sigma:
    # 2r = d = 2 * sqrt(2) * sigma => sigma = d / 2 * sqrt(2) ~ d / 2.83
    sigma = size/2.83 if sigma == 0 else sigma
    # 2d + normalize
    xx, yy = np.meshgrid(gx, gx)
    kernel2d = np.exp( -(xx**2 + yy**2) / (2 * sigma**2))
    kernel2d /= kernel2d.sum()
    return kernel2d

# Difference Of 2 Gaussians (i find so funny that is called 'dog')
def mk_dog(inner_size,outer_size,filter_size=0,inner_sigma=0,outer_sigma=0):
    inner_sigma = inner_size/2.83 if inner_sigma == 0 else inner_sigma
    outer_sigma = outer_size/2.83 if outer_sigma == 0 else outer_sigma
    filter_size = outer_size if filter_size == 0 else filter_size
    gx_inner = gauss2d(filter_size, inner_sigma)
    gx_outer = gauss2d(filter_size, outer_sigma)
    dog = gx_inner - gx_outer
    dog -= dog.mean()
    return dog

# TODO
# a bandpass filter made of the difference of 2 gaussians
# it applies 2 linear gaussians for speed
def dog_bandpassft(inner_size, outer_size, inner_sigma=0, outer_sigma=0):
    gx_inner = gauss1d(inner_size, inner_sigma)
    gx_outer = gauss1d(outer_size, outer_sigma)
    conv1 = np.apply_along_axis(lambda x: np.convolve(x, gx_inner, mode='reflect'), 1)
    pass


# TODO: check this
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