# -*- coding: utf-8 -*-

import os
import pandas as pd
import numpy as np
from auxs import get_dir_file_path, change_extension, mk_sep
from avi2tiff import count_avi_frames

dir_path = 'C:\\Users\\Fernando\\zf\\data\\2cams_movies'
fname = 'fish3.csv'
fpath = os.path.join(dir_path,fname)


def match_csv_rows(fpath,movie=[],nframes=0,with_pandas=False,return_df=False):
    df = pd.read_csv(fpath)
    dirpath, fname = get_dir_file_path(fpath)
    # pandas is slower
    if with_pandas:
        idxs = [0]
        for i in range(1,len(df)-1):
            if df.iloc[i]['Timestamp'] != df.iloc[i-1]['Timestamp']:
                idxs.append(i)
        df2 = pd.DataFrame(index=idxs, columns=df.columns)
        # drop last lines
    # numpy and export
    arr = df.to_numpy()
    qp = np.array([arr[ri] for ri in range(arr.shape[0]-1) if arr[ri][6] != arr[ri+1][6]])
    if nframes:
        qp = qp[:nframes]
    elif isinstance(movie, np.ndarray):
        qp = qp[:movie.shape[0]]
    else:
        tif_fname = change_extension(fname,new_ext='avi')
        tif_fpath = os.path.join(dirpath,tif_fname)
        nframes = count_avi_frames(tif_fpath)
        qp = qp[:nframes]
    # import pdb;pdb.set_trace()
    df2 = pd.DataFrame(qp, columns=df.columns)
    basename = change_extension(fname,'')
    sep = mk_sep()
    df2.to_csv(f'{dirpath}{sep}{basename}_tm.csv')
    if return_df:
        return df2

x = match_csv_rows(fpath,return_df=True)