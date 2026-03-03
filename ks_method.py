

import numpy as np
import tifffile as tf
# import matplotlib.pyplot as plt
# import matplotlib.gridspec as gridspec

from scipy.optimize import curve_fit
from scipy.ndimage import shift, gaussian_filter
from scipy.stats import ks_2samp
from skimage.registration import phase_cross_correlation
from skimage.feature import peak_local_max

import os
from scipy.ndimage import zoom
import pandas as pd

# ============================================================
# PARAMETERS
# ============================================================

class KS_pipeline:
    def __init__(self, fpath,
        percentile = 70,                # for peaks
        min_distance = 3,               # between pixel peaks
        roi_radius = 3,                 # radius for synapses
        sigma_smooth = 0,               # for gaussian filter in ΔF map
        sigma_fit = 1,                  # for 2d gaussian fit
        lambda_reg = 0.05,              # regul. strength in ridge regression
        baseline_windows = [(0,5), (55,60)],    # for baseline idxs
        freq = 20,                      # could be variable
        edge_margin = 3,                # could be variable
        alpha = 0.05,                   # threshold for p-value significance
        patch_radius = 3,               # ?
        baseline_window_dff = (1,5),    # ?
        #
        registration = True,
        bleach_correction = True,
        igor = True,
        debug = False
        ):
            self.fpath = fpath
            self.threshold_percentile = percentile
            self.min_distance = min_distance
            self.roi_radius = roi_radius
            self.sigma_smooth = sigma_smooth
            self.baseline_windows = baseline_windows
            self.alpha = alpha
            self.sigma_fit = sigma_fit
            self.lambda_reg = lambda_reg
            # this should be dynamic from igor info
            self.freq = freq
            # this could be dynamic (depends on reg type)
            self.edge_margin = edge_margin
            # ?
            # self.patch_radius = patch_radius
            # self.baseline_window_dff = (1,5)
            #
            self.igor = igor
            self.debug = debug
            self.run()

    def run(self):
        self.load_movie()
        self.register()
        self.interpolate()
        self.bleach_correction()
        self.stim_transitions()
        self.mk_deltaf_map()
        self.ks_distance()
        # in case there's no synapses found
        if isinstance(self.synapses,np.ndarray):
            self.ridge_demixing()
            self.compute_dff_traces()


    def load_movie(self):
        # assumes raw movie
        raw_movie = tf.imread(self.fpath)
        # de-interleave
        self.movie = raw_movie[0::2]
        self.nframes = self.movie.shape[0]
        # stimulus = raw_movie[1::2]
        # stimulus may be used later?
        # self.stimulus_trace = stimulus.mean(axis=(1,2))
        if self.debug:
            print('in load_movie()')
            import pdb; pdb.set_trace()
        if self.igor:
            self.mk_names()


    def mk_names(self):
        fdir = f'{os.path.sep}'.join(self.fpath.split(os.path.sep)[:-1])
        fname = self.fpath.split(os.path.sep)[-1].split('.')[0]
        savedir = os.path.join(fdir,'python_output')
        self.savepath = os.path.join(savedir,fname)
        if not os.path.isdir(savedir):
            os.mkdir(savedir)


    # i'm leaving this as independent in case we want
    # to try other registration methods
    def register(self, upsample_factor=10):
        reference = self.movie.mean(axis=0)
        movie_reg = np.zeros_like(self.movie)
        for i in range(self.nframes):
            shift_est,_,_ = phase_cross_correlation(reference, self.movie[i], upsample_factor=upsample_factor)
            movie_reg[i] = shift(self.movie[i], shift_est)
        # to avoid inheritance problems
        self.movie = movie_reg.copy()
        if self.debug:
            print('in register()')
            import pdb; pdb.set_trace()
        if self.igor:
            self.savepath += '_reg'
            tf.imwrite(f'{self.savepath}.tif', self.movie)


    def interpolate(self):
        # interpolates to make it squared (x = 128)
        zoom_ratio = self.movie.shape[2]/self.movie.shape[1]
        # order 1: bilinear
        self.movie = zoom(self.movie, zoom=(1,zoom_ratio,1), order=1)
        self.nrows, self.ncols = self.movie.shape[1:]
        if self.debug:
            print('in interpolate()')
            import pdb; pdb.set_trace()
        if self.igor:
            self.savepath += '_int'
            tf.imwrite(f'{self.savepath}.tif', self.movie)


    # TODO: i don't understand this totally, applies to CA?
    # correct for the bleaching of glutamate
    def bleach_correction(self):
        frame_mean = self.movie.mean(axis=(1,2))
        def exp_decay(t,A,tau,C):
            return A*np.exp(-t/tau)+C
        p0 = [frame_mean[0] - frame_mean[-1], self.nframes/self.freq/2, frame_mean[-1]]
        time = np.arange(self.nframes)/self.freq
        params,_ = curve_fit(exp_decay,time,frame_mean,p0=p0,maxfev=10000)
        fit_curve = exp_decay(time,*params)
        self.movie = self.movie / np.maximum(fit_curve[:,None,None],1e-8)
        if self.debug:
            print('in bleach_correction()')
            import pdb; pdb.set_trace()
        if self.igor:
            self.savepath += '_bc'
            tf.imwrite(f'{self.savepath}.tif', self.movie)


    # decouple baseline & activity
    def stim_transitions(self):
        # make baseline indices
        if len(self.baseline_windows) > 0:
            self.baseline_idxs = np.array([np.arange(a*self.freq,b*self.freq) for a,b in self.baseline_windows]).flatten()
        # remove baseline idxs from movie idxs for activivity idxs
        mask = np.ones((self.nframes)).astype(bool)
        mask[self.baseline_idxs] = False
        self.activity_idxs = np.arange(self.nframes)[mask]
        if self.debug:
            print('in stim_transitions()')
            import pdb; pdb.set_trace()


    # TODO: why is this before ks-distance?
    # TODO: is percentile the best threshold abs?
    # wouldn't that be threshold rel?
    # ΔF map + peak detection
    def mk_deltaf_map(self):
        baseline_mean = self.movie[self.baseline_idxs].mean(axis=0)
        activity_mean = self.movie[self.activity_idxs].mean(axis=0)
        deltaf_map = gaussian_filter(activity_mean - baseline_mean, sigma=self.sigma_smooth)
        # minimum intensity for pixels
        threshold_abs = np.percentile(deltaf_map, self.threshold_percentile)
        # local max in: 2 * min distance + 1
        self.deltaf_peaks = peak_local_max(deltaf_map,
                            min_distance=self.min_distance,
                            threshold_abs=threshold_abs,
                            exclude_border=self.edge_margin)
        if self.debug:
            print('in deltaf_map()')
            import pdb; pdb.set_trace()
        if self.igor:
            tf.imwrite(f'{self.savepath}_deltaf.tif', deltaf_map)


    # TODO: is not actually using the distance
    # TODO: if ROIs are averaged, shouldn't min_distance be 0/1? > test
    # TODO: study p-value thresholding
    # TODO: why there is a ΔF/F and a ΔF map?
    # TODO: make a ks map for igor
    # KS between ROIs (baseline vs activity)
    def ks_distance(self):
        self.ks_peaks = []
        # meshgrid for rows and cols
        yy, xx = np.indices((self.nrows, self.ncols))
        # make ROIs from pixels
        for y0,x0 in self.deltaf_peaks:
            # x^2 + y^2 = r^2
            mask = ((yy-y0)**2 + (xx-x0)**2) <= self.roi_radius**2
            # ΔF/F
            f0 = self.movie[self.baseline_idxs][:,mask].mean()
            f1 = self.movie[self.activity_idxs][:,mask].mean()
            dff = (f1-f0)/f0
            # vals: pixel vals in circular region around pixel across movie
            # [:,mask] doesn't preserve shape: returns 1d arr for each frame
            baseline_vals = self.movie[self.baseline_idxs][:,mask].mean(axis=1)
            activity_vals = self.movie[self.activity_idxs][:,mask].mean(axis=1)
            # ks
            dist,pval = ks_2samp(baseline_vals, activity_vals)
            self.ks_peaks.append([y0,x0,dff,dist,pval])
        # sort by p-vals
        self.ks_peaks = np.array(sorted(self.ks_peaks, key=lambda x:x[-1]))
        # threshold line
        th_line = self.alpha * np.arange(1, len(self.ks_peaks)+1)/len(self.ks_peaks)
        # remove where p-values > threshold line
        self.ks_peaks = self.ks_peaks[np.where(self.ks_peaks[:,-1] <= th_line)]
        # sort by ΔF/F and keep coords only
        if len(self.ks_peaks) == 0:
            # raise Exception ('\nNo significative peaks found\n')
            print('\nNo significative peaks found\n')
            self.synapses = None
            return
        self.synapses = np.array(sorted(self.ks_peaks, key=lambda x:x[2], reverse=True))[:,:2].astype(int)
        # export data
        if self.debug:
            print('in ks_distance()')
            import pdb; pdb.set_trace()
        if self.igor:
            df1 = pd.DataFrame(self.ks_peaks)
            df2 = pd.DataFrame(self.synapses)
            df1.to_csv(f'{self.savepath}_ks-peaks.csv')
            df2.to_csv(f'{self.savepath}_synapses.csv')


    # TODO: understand better the last part here
    # TODO: why is returning pixels instead of ROIs?
    # TODO: is it necessary to discard margins again?
    # 2 x 2d gaussians fit for demixing
    def ridge_demixing(self):
        # unzip, same as zip(*synapses)
        ys, xs = np.array(self.synapses).T
        # discard margins
        ymin = max(0, ys.min()-self.edge_margin)
        ymax = min(ys.max()+self.edge_margin, self.nrows)
        xmin = max(0, xs.min()-self.edge_margin)
        xmax = min(xs.max()+self.edge_margin, self.ncols)
        sy = ymax - ymin
        sx = xmax - xmin
        # for the gaussians
        gs_list = []
        yy, xx = np.indices((sy,sx))
        for y0,x0 in self.synapses:
            # creates a 2d gaussian centered around pixel
            gi = np.exp(-((xx-(x0-xmin))**2 + (yy-(y0-ymin))**2)/(2*self.sigma_fit**2))
            gs_list.append(gi.ravel())
        # array of flattended gaussians
        gs = np.column_stack(gs_list)
        # cov matrix - here @ is the same as .matmul()
        # each element (i,j) is the dot product between:
        # the gaussian of synape i and the gaussian of synapse j
        # so the diagonal: dot product with itself => size
        # off-diagonal: overlap among synapses
        gs_cov = gs.T @ gs
        # lambda reg adds a small value to the diagonal (* np.eye)
        # so too small makes the solution unstable
        # too large it looses signals (makes weights almost 0)
        gs_demix = np.linalg.solve(gs_cov + self.lambda_reg * np.eye(gs_cov.shape[0]), gs.T)
        # get amplitudes
        self.gs_amps = np.zeros((self.synapses.shape[0],self.nframes))
        for nf in range(self.nframes):
            frame = self.movie[nf,ymin:ymax,xmin:xmax].flatten()
            # 23 x (~128x128).flat @ (~128x128).flat x 1 => 23 x 1
            self.gs_amps[:,nf] = gs_demix @ frame
        if self.debug:
            print('in ridge_demix()')
            import pdb; pdb.set_trace()


    # TODO: why is there a different baseline window here?
    # TODO: check if tiff is best way to save
    # i assume is the same as only the first window?
    def compute_dff_traces(self):
        a,b = self.baseline_windows[0]
        baseline_idxs_dff = np.arange(a*self.freq,b*self.freq)
        # get traces
        self.dff_traces = []
        for i,amp in enumerate(self.gs_amps):
            f0 = np.median(amp[baseline_idxs_dff])
            self.dff_traces.append((amp-f0)/f0)
        self.dff_traces = np.array(self.dff_traces)
        # save
        if self.debug:
            print('in compute_dff_traces()')
            import pdb; pdb.set_trace()
        if self.igor:
            tf.imwrite(f'{self.savepath}_dff-traces.tif', self.dff_traces)



if __name__ == "__main__":
    movie = sys.argv[0]
    percentile = 70
    min_distance = 3
    roi_radius = 3
    sigma_mooth = 0
    sigma_fit = 3
    baseline_windows = [(0,5), (55,60)]
    debug = False
    for ei,arg in enumerate(sys.argv):
        if arg.startswith('--percentile='):
            percentile = float(arg.split('=')[1])
        if arg.startswith('--min_distance='):
            min_distance = float(arg.split('=')[1])
        if arg.startswith('--roi_radius='):
            roi_radius = float(arg.split('=')[1])
        if arg.startswith('--patch_radius='):
            patch_radius = float(arg.split('=')[1])
        if arg.startswith('--sigma_smooth='):
            sigma_smooth = float(arg.split('=')[1])
        if arg.startswith('--sigma_fit='):
            sigma_fit = float(arg.split('=')[1])
        if arg.startswith('--baseline_windows='):
            baseline_windows = arg.split('=')[1]
        if arg == '--debug':
            debug == True
        if arg == '--igor':
            igor = True
    ks_run(path_to_movie=movie, debug=debug,
        percentile=percentile,
        min_distance=min_distance,
        roi_radius=roi_radius,
        patch_radius=patch_radius,
        sigma_fit=sigma_fit,
        baseline_windows=baseline_windows
        )









#
