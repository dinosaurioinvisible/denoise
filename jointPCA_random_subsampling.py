#!/usr/bin/env python3
# -*- coding: utf-8 -*-


import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
import matplotlib.pyplot as plt
import seaborn as sns
from tqdm import tqdm


# load csv data as dfs
rest = pd.read_csv('/Users/f/Desktop/data antonio/combined_rest_reduced_good_3_05.csv')
loco = pd.read_csv('/Users/f/Desktop/data antonio/combined_reduced_Loco_Opto.csv')
rest["condition"] = "rest"
loco["condition"] = "loco"

joint = pd.concat([rest, loco], ignore_index=True)

weights_cols = [f'w_{i}' for i in range(19)]
pc_cols = [f"PC{i+1}" for i in range(19)]
n_reps = 10000
# for checking repeats
sampled_subsets = set()
# to save data
subsets_indexes = []
pca_exp_vars = []
pca_mean_diffs = []
pc1_loads = []

nr = 0
pbar = tqdm(total=n_reps)
while nr < n_reps:
    rest_subset = rest.sample(n=len(loco), replace=False)
    # check if not previously sampled
    subset_indexes = tuple(sorted(rest_subset.index))
    if subset_indexes in sampled_subsets:
        # skip to next iteration
        continue
    sampled_subsets.add(subset_indexes)
    subsets_indexes.append(subset_indexes)
    
    # merge, get weights, scale & run PCA
    joint = pd.concat([rest_subset,loco], ignore_index=True)
    weights = joint[weights_cols].values
    scaler = StandardScaler()
    scaled_weights = scaler.fit_transform(weights)
    pca = PCA()
    weights_pca = pca.fit_transform(scaled_weights)

    # append PComponents back to df
    for i in range(weights_pca.shape[1]):
        joint[f'PC{i+1}'] = weights_pca[:,i]

    # mean differences between rest & locomotion elements
    means = joint.groupby("condition")[pc_cols].mean()
    mean_diffs = means.loc["loco"] - means.loc["rest"]
    pc1_loadings = pca.components_[0].copy()

    # make locomotion always positive & rest negative
    if mean_diffs["PC1"] < 0:
        weights_pca[:, 0] *= -1
        pca.components_[0] *= -1
        mean_diffs["PC1"] *= -1
        pc1_loadings *= -1
    
    # save results
    pca_exp_vars.append(pca.explained_variance_ratio_)
    pca_mean_diffs.append(mean_diffs)
    pc1_loads.append(pc1_loadings)
    nr += 1
    pbar.update(1)

pbar.close()
# to pandas  
pca_results = pd.DataFrame( pca_exp_vars, columns=[f"PC{i}_var" for i in range(19)])
pca_diffs = pd.DataFrame(pca_mean_diffs,columns=pc_cols)
pc1_loads = pd.DataFrame(pc1_loads,columns=weights_cols)

# summary tables
print("Average explained variance:")
print(pca_results.mean().sort_values(ascending=False))

print("Average loco-rest difference:")
print(pca_diffs.mean().sort_values(key=abs, ascending=False))

print("Explained variance summary:")
print(pca_results.describe())

print("Mean difference summary:")
print(pca_diffs.describe())

print("PC1 loadings summary:")
print(pc1_loads.describe())

# plot explained variances
plt.figure(figsize=(10, 5))
sns.boxplot(data=pca_results)
plt.xticks(rotation=45)
plt.ylabel("Explained variance ratio")
plt.xlabel("Principal component")
plt.title("Explained variance across balanced PCA repetitions")
plt.tight_layout()
plt.show()
    
# plot cumulative pca results (var exp)
n = 7
cum_pca_results = pca_results.cumsum(axis=1)
mean_cum = cum_pca_results.mean(axis=0)
std_cum = cum_pca_results.std(axis=0)
x = np.arange(1, len(mean_cum) + 1)
plt.figure(figsize=(8, 5))
plt.plot(x, mean_cum, "o-", label="Mean cumulative variance")
plt.fill_between(x,
    mean_cum - std_cum,
    mean_cum + std_cum,
    alpha=0.2,
    label="±1 SD")
plt.axhline(mean_cum.iloc[n], linestyle="--", color='orange', label=f'PC1-PC{n}')
plt.axhline(0.99, linestyle="--", color='red', label='0.99')
plt.xlabel("Number of PCs")
plt.ylabel("Cumulative explained variance")
plt.title("Cumulative explained variance across repetitions")
plt.legend()
plt.tight_layout()
plt.show()

# locomotion vs rest, for each PC
plt.figure(figsize=(10, 5))
sns.boxplot(data=pca_diffs)
plt.axhline(0, linestyle="--")
plt.xticks(rotation=45)
plt.ylabel("Mean differences: loco - rest")
plt.xlabel("Principal component")
plt.title("Locomotion-rest mean difference across PCA repetitions")
plt.tight_layout()
plt.show()

# prob distribution of PC1 mean diffs
plt.figure(figsize=(7, 5))
sns.histplot(abs(pca_diffs["PC1"]), kde=True)
# plt.axvline(0, linestyle="--")
plt.xlabel("PC1 mean differences: loco - rest")
plt.ylabel("Count")
plt.title("Distribution of PC1 across repetitions")
plt.tight_layout()
plt.show()

# mean values for loadings of PC1
mean_pc1_loadings = pc1_loads.mean(axis=0)
plt.figure(figsize=(10, 5))
mean_pc1_loadings.plot(kind="bar")
plt.axhline(0, linestyle="--")
plt.ylabel("Mean PC1 loading")
plt.xlabel("Weight")
plt.title("Mean PC1 loadings across balanced PCA repetitions")
plt.tight_layout()
plt.show()













    
    
    
    