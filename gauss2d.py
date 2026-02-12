

# igor:
# Pawel: PSF of microscope has width 1um => x_width = 1 & y_width = 1
# (i guess this is for the sigmas)
# coef_wave[0]+coef_wave[1]*exp((-1/(2*(1-coef_wave[6]^2)))*(((x-coef_wave[2])/coef_wave[3])^2 + ((y-coef_wave[4])/coef_wave[5])^2 - (2*coef_wave[6]*((y-coef_wave[4])*(x-coef_wave[2]))/(coef_wave[3]*coef_wave[5]))))

import numpy as np
from scipy.optimize import curve_fit

def twoD_Gaussian(xy, amplitude, xo, yo, sigma_x, sigma_y, theta, offset):
    x, y = xy
    xo = float(xo)
    yo = float(yo)
    a = (np.cos(theta)**2)/(2*sigma_x**2) + (np.sin(theta)**2)/(2*sigma_y**2)
    b = -(np.sin(2*theta))/(4*sigma_x**2) + (np.sin(2*theta))/(4*sigma_y**2)
    c = (np.sin(theta)**2)/(2*sigma_x**2) + (np.cos(theta)**2)/(2*sigma_y**2)
    g = offset + amplitude*np.exp(-(a*((x-xo)**2) + 2*b*(x-xo)*(y-yo) + c*((y-yo)**2)))
    return g.ravel()

def fit_gaussian2d_amplitude(Z, r0, c0, halfwin=2):
    """
    Fit a rotated 2D Gaussian to a small window around (r0, c0) in array Z,
    and return the fitted amplitude (plus other fit outputs if you want them).

    Z   : 2D array (image)
    r0  : row index of point of interest
    c0  : col index of point of interest
    halfwin : window radius in pixels (window size = 2*halfwin+1)
    """
    # ---- extract patch ----
    r1, r2 = max(0, r0-halfwin), min(Z.shape[0], r0+halfwin+1)
    c1, c2 = max(0, c0-halfwin), min(Z.shape[1], c0+halfwin+1)
    patch = Z[r1:r2, c1:c2]

    # ---- coordinate grid in image coords: x=col, y=row ----
    y = np.arange(r1, r2)
    x = np.arange(c1, c2)
    x, y = np.meshgrid(x, y)

    # ---- initial guesses ----
    offset0 = float(np.median(patch))
    amplitude0 = float(patch.max() - offset0)   # for bright peaks
    xo0, yo0 = float(c0), float(r0)
    sigma0 = float(max(1.0, halfwin/2))
    theta0 = 0.0

    p0 = (amplitude0, xo0, yo0, sigma0, sigma0, theta0, offset0)

    # ---- bounds (recommended) ----
    lower = (-np.inf, c1-1, r1-1, 0.3, 0.3, -np.pi/2, -np.inf)
    upper = ( np.inf, c2,   r2,   2*halfwin, 2*halfwin, np.pi/2,  np.inf)

    # ---- fit ----
    popt, pcov = curve_fit(
        twoD_Gaussian,
        (x, y),
        patch.ravel(),
        p0=p0,
        bounds=(lower, upper),
        maxfev=20000
    )

    amplitude = popt[0]
    offset = popt[6]
    peak_value = amplitude + offset

    return amplitude, peak_value, popt, pcov

# ------------------- example -------------------
# Z = ... your 2D array ...
# r0, c0 = 120, 80
# amp, peak, popt, pcov = fit_gaussian2d_amplitude(Z, r0, c0, halfwin=6)
# print("Amplitude:", amp)
# print("Peak value (offset + amplitude):", peak)

# Source - https://stackoverflow.com/a/21566831
# def twoD_Gaussian(row,col,amplitude, x0=None, y0=None, sigma_x=1, sigma_y=1, theta=0, offset=0):
#     x, y = col,row
#     x0 = float(x) if not x0 else float(x0)
#     y0 = float(y) if not y0 else float(y0)
#     a = (np.cos(theta)**2)/(2*sigma_x**2) + (np.sin(theta)**2)/(2*sigma_y**2)
#     b = -(np.sin(2*theta))/(4*sigma_x**2) + (np.sin(2*theta))/(4*sigma_y**2)
#     c = (np.sin(theta)**2)/(2*sigma_x**2) + (np.cos(theta)**2)/(2*sigma_y**2)
#     g = offset + amplitude*np.exp( - (a*((x-x0)**2) + 2*b*(x-x0)*(y-y0) + c*((y-y0)**2)))
#     return g.ravel()



#
