#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import numpy as np
import numpy as np

def fiji_fft_bandpass_anisotropic(
    image,
    dx, dy,                 # pixel size: physical units per pixel (x, y)
    filter_small,           # smallest structures to keep (same physical units)
    filter_large,           # largest structures to keep (same physical units)
    soft=False,
    softness=0.05           # softness in same units as frequency (see note below)
):
    """
    Fiji-like 2D FFT bandpass, but with anisotropic pixel sizes.

    image: 2D array
    dx, dy: physical pixel size in x and y (e.g., microns per pixel)
    filter_small: smallest structure size to keep (e.g., microns)
    filter_large: largest structure size to keep (e.g., microns)
    soft: if True, use a smooth (logistic) mask to reduce ringing
    """

    rows, cols = image.shape

    # FFT
    F = np.fft.fftshift(np.fft.fft2(image))

    # Spatial frequency axes in physical units (cycles per unit distance)
    fy = np.fft.fftshift(np.fft.fftfreq(rows, d=dy))
    fx = np.fft.fftshift(np.fft.fftfreq(cols, d=dx))
    FX, FY = np.meshgrid(fx, fy)

    # Radial spatial frequency in physical frequency space
    R = np.sqrt(FX**2 + FY**2)

    # Convert feature sizes -> cutoff frequencies
    f_low  = 1.0 / filter_large   # remove large structures (low freq)
    f_high = 1.0 / filter_small   # remove small structures (high freq)

    if not soft:
        mask = (R >= f_low) & (R <= f_high)
        Ff = F * mask
    else:
        # Smooth “ring” mask using logistic transitions
        # softness controls transition width in frequency units (cycles per physical unit)
        low_ramp  = 1.0 / (1.0 + np.exp(-(R - f_low)  / softness))
        high_ramp = 1.0 / (1.0 + np.exp( (R - f_high) / softness))
        mask = low_ramp * high_ramp
        Ff = F * mask

    # Inverse FFT
    filtered = np.fft.ifft2(np.fft.ifftshift(Ff))
    return np.real(filtered)