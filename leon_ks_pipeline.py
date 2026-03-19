# -*- coding: utf-8 -*-

import numpy as np
import tifffile as tiff
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec

from scipy.optimize import curve_fit
from scipy.ndimage import shift, gaussian_filter
from scipy.stats import ks_2samp
from skimage.registration import phase_cross_correlation
from skimage.feature import peak_local_max

# ============================================================
# PARAMETERS
# ============================================================
fs = 20.0

baseline_windows = [(0,5), (55,60)]
transition_window_sec = 1
threshold_percentile = 70
min_distance = 3
roi_radius = 3

sigma_smooth = 0
edge_margin = 3
patch_radius = 3
alpha = 0.05

baseline_window_dff = (1,5)

sigma_fit = 1

# new images from jose
# 090226: CTRL
# fpath = '/Users/f/Desktop/090226/F2/CTR/CR_1HZ_AF10_CTRL.tif'
#fpath = '/Users/f/Desktop/090226/F2/CTR/STEP_AF10_CTRL.tif'
# fpath = '/Users/f/Desktop/090226/F2/CTR/TF_AF10_CTRL.tif'
# 090226: STR
# fpath = '/Users/f/Desktop/090226/F2/STR/CR_1HZ_AF10_STR.tif'
# fpath = '/Users/f/Desktop/090226/F2/STR/STEP_1HZ_AF10_STR.tif'
# fpath = '/Users/f/Desktop/090226/F2/STR/TF_AF10_STR.tif'
# # 100226: F1 - CTRL
# fpath = '/Users/f/Desktop/100226/F1/CTRL/CR_1HZ_AF10001_CTRL.tif'
# fpath = '/Users/f/Desktop/100226/F1/CTRL/STEP_AF10002_CTRL.tif'
# fpath = '/Users/f/Desktop/100226/F1/CTRL/TF_AF10003_CTRL.tif'
# # 100226: F1 - STR
# fpath = '/Users/f/Desktop/100226/F1/STR/CR_1HZ_AF10016_STR.tif'
fpath = '/Users/f/Desktop/100226/F1/STR/STEP_AF10017_STR.tif'
# fpath = '/Users/f/Desktop/100226/F1/STR/TF_AF10018-STR.tif'
# # 100226: F2 - CTRL
# fpath = '/Users/f/Desktop/100226/F2/CTRL/CR_1HZ_AF10007_CTRL.tif'
# fpath = '/Users/f/Desktop/100226/F2/CTRL/STEP_AF10008_CTRL.tif'
# fpath = '/Users/f/Desktop/100226/F2/CTRL/TF_AF10009_CTRL.tif'
# # 100226: F2 - STR
# fpath = '/Users/f/Desktop/100226/F2/STR/CR_1HZ_AF10_STR.tif'
# fpath = '/Users/f/Desktop/100226/F2/STR/STEP_AF10_STR020.tif'
# fpath = '/Users/f/Desktop/100226/F2/STR/TF_AF10_STR022.tif'
# # 100226: F3 - CTRL
# fpath = '/Users/f/Desktop/100226/F3/CTRL/CR_1HZ_AF10013.tif'
# fpath = '/Users/f/Desktop/100226/F3/CTRL/STEP_AF10014.tif'
# fpath = '/Users/f/Desktop/100226/F3/CTRL/TF_AF10015.tif'
# # 100226: F3 - STR
# fpath = '/Users/f/Desktop/100226/F3/STR/CR_1HZ_AF10_STR023.tif'
# fpath = '/Users/f/Desktop/100226/F3/STR/STEP_1HZ_AF10_STR024.tif'
# fpath = '/Users/f/Desktop/100226/F3/STR/TF_1HZ_AF10_STR025.tif'

# good
# fpath = 'C:\\Users\\Fernando\\zf\\data\\jose_data\\Calcium_Tectum\\111125_CA_HUC\\f1\\a1\\step_HUC_a1.tif'
# fpath = 'C:\\Users\\Fernando\\zf\\data\\jose_data\\Glutamate_Tectum\\F2_glut_HUC_AF10\\A1\\Steps_pre_AF10_a1015_interpol.tif'
# fpath = 'C:\\Users\\Fernando\\zf\\data\\jose_data\\Glutamate_Tectum\\F2_glut_HUC_AF10\\A1\\Steps_pre_AF10_a1015_interpol.tif'
# fpath = 'C:\\Users\\Fernando\\zf\\data\\jose_data\\Glutamate_Tectum\\F7_glut_HUC_AF10\\steps_pre_AF10_a1039.tif'
# fpath = 'C:\\Users\\Fernando\\zf\\data\\jose_data\\Glutamate_Tectum\\F5_glut_HUC_AF10\\a1\\STEP_AF10_a1012.tif'
# fpath = 'C:\\Users\\Fernando\\zf\\data\\jose_data\\Glutamate_Tectum\\F5_glut_HUC_AF10\\a2\\STEPS_AF10_a2017.tif'
# fpath = 'C:\\Users\\Fernando\\zf\\data\\jose_data\\Glutamate_Tectum\\F6_glut_HUC_AF10\\a1\\steps_pre_AF10_a1029_interpol.tif'
# bad
# fpath = 'C:\\Users\\Fernando\\zf\\data\\jose_data\\Glutamate_Tectum\\F1_glut_HUC_AF10\\a1\\steps_pre_AF10_a1001.tif'

# fpath = '/Users/f/Dropbox/_r66y/r66xe/2p_data/glu_a2/Steps_pre_AF10_a1014.tif'

# ============================================================
# 1. LOAD + DEINTERLEAVE + INTERPOLATE
# ============================================================
interleaved = tiff.imread(fpath)

# T_total, Y, X = interleaved.shape
T_total = interleaved.shape[0]
if T_total % 2 != 0:
    raise ValueError("Interleaved movie must have even number of frames.")

movie_raw = interleaved[0::2]
stim_movie = interleaved[1::2]

T = movie_raw.shape[0]
time = np.arange(T)/fs


# ============================================================
# 2. REGISTRATION
# ============================================================
reference = movie_raw.mean(axis=0)
movie_reg = np.zeros_like(movie_raw)

for i in range(T):
    shift_est,_,_ = phase_cross_correlation(reference, movie_raw[i], upsample_factor=10)
    movie_reg[i] = shift(movie_raw[i], shift_est)


from scipy.ndimage import zoom

# order=1: bilinear interpolation
zoom_ratio = movie_reg.shape[2]/movie_reg.shape[1]
movie_int = zoom(movie_reg, zoom=(1,zoom_ratio,1), order=1)
Y, X = movie_int.shape[1:]

# ============================================================
# 3. BLEACH CORRECTION
# ============================================================
frame_mean = movie_int.mean(axis=(1,2))

def exp_decay(t,A,tau,C):
    return A*np.exp(-t/tau)+C

p0 = [frame_mean[0]-frame_mean[-1], T/fs/2, frame_mean[-1]]
params,_ = curve_fit(exp_decay,time,frame_mean,p0=p0,maxfev=10000)
fit_curve = exp_decay(time,*params)

movie_corr = movie_int / np.maximum(fit_curve[:,None,None],1e-8)

# ============================================================
# TODO: ASK LEON: not sure which points he wanted to get(?)
# 4. STIM TRANSITIONS
# ============================================================

stim_trace = stim_movie.mean(axis=(1,2))
# stim_binary = stim_trace > np.median(stim_trace)
# transitions = np.where(np.diff(stim_binary.astype(int))!=0)[0]

baseline_idx=[]
for s,e in baseline_windows:
    baseline_idx.extend(range(int(s*fs),int(e*fs)))
baseline_idx=np.array(baseline_idx)
# baseline_idx = baseline_idx[:100]

# transition_frames = int(transition_window_sec*fs)
# transition_idx=[]
# for idx in transitions:
#     start=idx+1
#     end=start+transition_frames
#     if end<T:
#         transition_idx.extend(range(start,end))
# transition_idx=np.array(transition_idx)

# alt
# if True:
#     plt.plot(stim_trace)
#     plt.plot(transitions.size)
#     plt.scatter(transitions, np.ones((transitions.size))*np.median(stim_trace))

# from utils.auxs import mk_steps
# stim_trace_steps = mk_steps(stim_trace, baseline=False)
# transitions = stim_trace_steps[np.where(stim_trace_steps==2)[0]]
# transition_idx = []
# for i0,i1,v in transitions:
#     transition_idx.extend(np.arange(i0,i1))
# transition_idx = np.array(transition_idx).astype(int)

# basically the code above would've returned every frame not part of the baseline, so:
act_start = baseline_windows[0][1]*fs
act_end = baseline_windows[1][0]*fs
transition_idx = np.arange(act_start,act_end).astype(int)


# ============================================================
# 5. ΔF MAP + PEAK DETECTION
# ============================================================
mean_base = movie_corr[baseline_idx].mean(axis=0)
mean_trans = movie_corr[transition_idx].mean(axis=0)
delta_map = gaussian_filter(mean_trans - mean_base, sigma=sigma_smooth)

threshold_abs = np.percentile(delta_map, threshold_percentile)

coords = peak_local_max(
    delta_map,
    min_distance=min_distance,
    threshold_abs=threshold_abs,
    exclude_border=edge_margin
)

# filtered_coords=[]
# for y0,x0 in coords:
#     if (y0>edge_margin and y0<Y-edge_margin and
#         x0>edge_margin and x0<X-edge_margin):
#         filtered_coords.append((y0,x0))

# ============================================================
# 6. KS + FDR
# ============================================================
pvals=[]
peaks=[]

rr_full,cc_full = np.indices((Y,X))

# for y0,x0 in filtered_coords:
for y0,x0 in coords:
    mask = ((rr_full-y0)**2+(cc_full-x0)**2)<=roi_radius**2

    base_vals = movie_corr[baseline_idx][:,mask].mean(axis=1)
    trans_vals = movie_corr[transition_idx][:,mask].mean(axis=1)

    D,p = ks_2samp(base_vals,trans_vals)

    pvals.append(p)
    peaks.append((y0,x0,D,p))

pvals=np.array(pvals)
significant=[]

if len(pvals)>0:
    # sorts indices
    idx_sorted=np.argsort(pvals)
    # sorts values
    sorted_p=pvals[idx_sorted]
    # TODO
    # don't understand this really:
    # is it a procedure for p-values?
    m=len(sorted_p)
    threshold_line=alpha*np.arange(1,m+1)/m
    significant_mask=sorted_p<=threshold_line

    if np.any(significant_mask):
        # max index among those < threshold line
        max_i=np.where(significant_mask)[0].max()
        # value of max index in sorted_p, so max value
        p_cutoff=sorted_p[max_i]
        # select peaks < max p value
        for i,(y0,x0,D,p) in enumerate(peaks):
            if p<=p_cutoff:
                significant.append((y0,x0))

# ============================================================
# 7. BUILD SYNAPSE LIST
# ============================================================
synapses=[]

for y0,x0 in significant:
    sigma_fit = sigma_fit
    rr,cc = np.indices((Y,X))
    mask = ((rr-y0)**2+(cc-x0)**2)<=roi_radius**2

    F0 = movie_corr[baseline_idx][:,mask].mean()
    F1 = movie_corr[transition_idx][:,mask].mean()
    dff_detect = (F1-F0)/F0

    synapses.append((y0,x0,sigma_fit,dff_detect))

# ============================================================
# 7b. CLEAN DETECTED SYNAPSES IMAGE
# ============================================================

plt.figure(figsize=(12,4))

vmin = np.percentile(delta_map, 5)
vmax = np.percentile(delta_map, 99)

plt.imshow(delta_map, cmap='gray', vmin=vmin, vmax=vmax)
plt.title(f"Detected Synapses (n={len(synapses)})")
plt.axis('off')

for i,(y0,x0,_,_) in enumerate(synapses, 1):

    plt.scatter(x0, y0,
                s=70,
                facecolors='none',
                edgecolors='red',
                linewidths=1.2)

    plt.text(x0, y0,
             str(i),
             color='yellow',
             fontsize=8,
             ha='center',
             va='center',
             fontweight='bold')

plt.tight_layout()
plt.show()

# ============================================================
# 8. SELECT TOP 5
# ============================================================
indexed_synapses = [
    (i+1, y0, x0, sigma_fit, dff_detect)
    for i,(y0,x0,sigma_fit,dff_detect) in enumerate(synapses)
]

indexed_synapses_sorted = sorted(indexed_synapses,
                                 key=lambda x: abs(x[4]),
                                 reverse=True)

top_synapses = indexed_synapses_sorted[:5]

# ============================================================
# 9. RIDGE DEMIXING
# ============================================================
ys = [y for y,_,_,_ in synapses]
xs = [x for _,x,_,_ in synapses]

margin = edge_margin
y_min = max(0, min(ys) - margin)
y_max = min(Y, max(ys) + margin)
x_min = max(0, min(xs) - margin)
x_max = min(X, max(xs) + margin)

subY = y_max - y_min
subX = x_max - x_min

G_list=[]

for y0,x0,sigma_fit,_ in synapses:
    yy,xx = np.indices((subY,subX))
    G_i = np.exp(-((xx-(x0-x_min))**2 + (yy-(y0-y_min))**2)/(2*sigma_fit**2))
    G_list.append(G_i.ravel())

G = np.column_stack(G_list)

lambda_reg = 0.05
GtG = G.T @ G
W = np.linalg.solve(GtG + lambda_reg*np.eye(GtG.shape[0]), G.T)

A_all = np.zeros((len(synapses), T))

for t in range(T):
    frame = movie_corr[t,y_min:y_max,x_min:x_max].ravel()
    A_all[:,t] = W @ frame

# ============================================================
# 10. COMPUTE ΔF/F TRACES
# ============================================================
baseline_idx_dff = np.where(
    (time >= baseline_window_dff[0]) &
    (time <= baseline_window_dff[1])
)[0]

all_dff_traces=[]
for i in range(len(synapses)):
    amp = A_all[i]
    F0 = np.median(amp[baseline_idx_dff])
    all_dff_traces.append((amp - F0)/F0)

all_dff_traces = np.array(all_dff_traces)

# Top 5 traces
dff_traces=[]
labels=[]
for syn_index,y,x,sigma,_ in top_synapses:
    dff_traces.append(all_dff_traces[syn_index-1])
    labels.append(f"Synapse {syn_index}")

# ============================================================
# 11. TOP 5 PLOT + STIM
# ============================================================
fig = plt.figure(figsize=(10,7))
gs = gridspec.GridSpec(20,1)

ax_main = fig.add_subplot(gs[:19,0])
for trace,label in zip(dff_traces,labels):
    ax_main.plot(time, trace, label=label)
ax_main.legend()
ax_main.set_ylabel("ΔF/F")

ax_stim = fig.add_subplot(gs[19,0],sharex=ax_main)
stim_norm = (stim_trace-stim_trace.min())/(stim_trace.max()-stim_trace.min())
ax_stim.fill_between(time,0,stim_norm,step='post',color='black')
ax_stim.axis('off')

plt.tight_layout()
plt.show()

# ============================================================
# 12. HEATMAP + STIM
# ============================================================
strength = np.max(np.abs(all_dff_traces),axis=1)
order = np.argsort(strength)[::-1]
sorted_traces = all_dff_traces[order]

fig = plt.figure(figsize=(10,7))
gs = gridspec.GridSpec(20,1)

ax_heat = fig.add_subplot(gs[:19,0])
vmax=np.percentile(np.abs(sorted_traces),99)
ax_heat.imshow(sorted_traces,aspect='auto',cmap='gray',
               vmin=-vmax,vmax=vmax)

ax_stim = fig.add_subplot(gs[19,0],sharex=ax_heat)
ax_stim.fill_between(time,0,stim_norm,step='post',color='black')
ax_stim.axis('off')

plt.tight_layout()
plt.show()



# ============================================================
# 13. QUANTIFY SPATIAL CROSS-TALK
# ============================================================

# ---- Independent traces (no demixing) ----
independent_traces = []

for y0,x0,sigma_fit,_ in synapses:

    rr,cc = np.indices((Y,X))
    mask = ((rr-y0)**2+(cc-x0)**2)<=roi_radius**2

    amp = movie_corr[:,mask].mean(axis=1)
    F0 = np.median(amp[baseline_idx_dff])
    dff = (amp - F0) / F0

    independent_traces.append(dff)

independent_traces = np.array(independent_traces)

# ---- Ridge-demixed traces (already computed) ----
ridge_traces = all_dff_traces.copy()

# ---- Correlation matrices ----
corr_ind = np.corrcoef(independent_traces)
corr_ridge = np.corrcoef(ridge_traces)

# ---- Spatial distances ----
coords = np.array([(y,x) for y,x,_,_ in synapses])

dist_matrix = np.sqrt(
    (coords[:,None,0] - coords[None,:,0])**2 +
    (coords[:,None,1] - coords[None,:,1])**2
)

# ---- Neighbour pairs (< 6 pixels apart) ----
distance_threshold = 6
mask_pairs = (dist_matrix > 0) & (dist_matrix < distance_threshold)

neighbor_corr_ind = corr_ind[mask_pairs]
neighbor_corr_ridge = corr_ridge[mask_pairs]

print("Mean neighbour correlation (Independent):",
      np.mean(neighbor_corr_ind))

print("Mean neighbour correlation (Ridge):",
      np.mean(neighbor_corr_ridge))
plt.figure(figsize=(8,4))

plt.hist(neighbor_corr_ind, bins=20, alpha=0.5, label="Independent")
plt.hist(neighbor_corr_ridge, bins=20, alpha=0.5, label="Ridge")

plt.xlabel("Pairwise Correlation (Neighbouring Synapses)")
plt.ylabel("Count")
plt.legend()
plt.title("Spatial Cross-Talk Comparison")
plt.tight_layout()
plt.show()
