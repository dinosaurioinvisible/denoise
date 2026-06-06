#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
import matplotlib.pyplot as plt
import seaborn as sns


# load csv data as dfs
rest = pd.read_csv('/Users/f/Desktop/data antonio/combined_rest_reduced_good_3_05.csv')
loco = pd.read_csv('/Users/f/Desktop/data antonio/combined_reduced_Loco_Opto.csv')
rest["condition"] = "rest"
loco["condition"] = "loco"

joint = pd.concat([rest, loco], ignore_index=True)

weights_cols = [f'w_{i}' for i in range(19)]

weights = joint[weights_cols].values

scaler = StandardScaler()
scaled_weights = scaler.fit_transform(weights)

pca = PCA()
weights_pca = pca.fit_transform(scaled_weights)

# number of PCs to check on scatter
n = 7

# cumulative explained variance
exp_var = pca.explained_variance_ratio_
cum_exp_var = np.cumsum(exp_var)

# cumulative plot
plt.plot(np.cumsum(pca.explained_variance_ratio_), "o-")
# arbitrary n, to avoid making so many plots
plt.axhline(cum_exp_var[n], linestyle="--", color='orange', label=f'PC1-{n}')
# plt.axhline(0.9, linestyle="--")
plt.axhline(0.99, linestyle="--", color='red', label='0.99')
plt.xlabel("Number of PCs")
plt.ylabel("Cumulative explained variance")
plt.legend()
plt.show()

# append PComponents back to df
for i in range(weights_pca.shape[1]):
    pci = f'PC{i+1}'
    joint[pci] = weights_pca[:,i]

# comparison among main components
# so the difference between rest and locomotion
for i in range(1,n+1):
    for j in range(i+1,n+1):
        pcx = f'PC{i}'
        pcy = f'PC{j}'
        if i < j:
            sns.scatterplot(data=joint, x=pcx, y=pcy, hue="condition", alpha=0.5)
            plt.show()

# everything seems to be explained by 1 (vs any other)
# to confirm: split each PC into rest and loco
# we can first comapre the means
pc_cols = [f"PC{i+1}" for i in range(19)]
means = joint.groupby("condition")[pc_cols].mean()
diff = means.loc["loco"] - means.loc["rest"]
print(diff)

# PC1 is by far the larger difference
# to compare the variability:
# cohen d is standard difference between 2 means
# > 1 is super large
def cohens_d(x, y):
    nx = len(x)
    ny = len(y)
    sx = x.std()
    sy = y.std()
    pooled_sd = np.sqrt(((nx - 1)*sx**2 + (ny - 1)*sy**2) / (nx + ny - 2))
    return (x.mean() - y.mean()) / pooled_sd

print("\n")
for pc in pc_cols:
    rest_vals = joint[joint["condition"] == "rest"][pc]
    loco_vals = joint[joint["condition"] == "loco"][pc]
    d = cohens_d(loco_vals, rest_vals)
    print(pc, d)

# which weights are more important: composition of PC1
loadings = pd.DataFrame(pca.components_,columns=weights_cols,
                index=[f"PC{i+1}" for i in range(19)])

print('\nsorted loadings:')
x = loadings.loc["PC1"]
x = x.reindex(x.abs().sort_values(ascending=False).index)
print(x)


























#





