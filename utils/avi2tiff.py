# -*- coding: utf-8 -*-

import os, sys
import cv2
from tqdm import tqdm
from auxs import change_extension, get_dir_file_path, mk_sep
from loading import file_menu
import tifffile as tf
import pandas as pd
import numpy as np

def count_avi_frames(fpath):
    cap = cv2.VideoCapture(fpath)
    nframes = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    cap.release()
    return nframes

def avi2tiff(fpath):
    cap = cv2.VideoCapture(fpath)
    frames = []
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        frame_gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        frames.append(frame_gray)
    farray = np.array(frames)
    return farray

def export_csv_rm_extra_lines(fpath_csv,fpath_movie,new_path=''):
    df = pd.read_csv(fpath_csv)
    nframes = count_avi_frames(fpath_movie)
    arr = df.to_numpy()
    arr = arr[:nframes]
    df2 = pd.DataFrame(arr, columns=df.columns)
    fdir,fname = get_dir_file_path(fpath_csv)
    basename = change_extension(fname,'')
    sep = mk_sep()
    if new_path:
        df2.to_csv(new_path)
    else:
        df2.to_csv(f'{dirpath}{sep}{basename}_match.csv')
    
def export_avi2tiff(fpath, overwrite=True):
    fdir,fname = get_dir_file_path(fpath)
    cap = cv2.VideoCapture(fpath)
    size = 6000
    nframes = 0
    basename = change_extension(fname,'')
    new_fdir = os.path.join(fdir,basename)
    
    if not os.path.isdir(new_fdir):
        os.mkdir(new_fdir)
    keep = True
    nframes_end = count_avi_frames(fpath)
    while keep:
        frames = []
        frames_start = nframes
        nframes_cycle = min(nframes+size,nframes_end)
        for _ in tqdm(range(nframes,nframes_cycle)):  
            ret, frame = cap.read()
            if not ret:
                keep = False
                break
            frame_gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            frames.append(frame_gray)
            nframes += 1
        farray = np.array(frames)
    
        keep = False if nframes >= nframes_end else keep
        new_fname = f'{basename}_{frames_start}-{nframes}.tiff'
        save_fpath = os.path.join(new_fdir,new_fname)
        if not os.path.isfile(save_fpath) or overwrite == True:
            tf.imwrite(save_fpath, farray)
            print(f'file saved at {save_fpath} - number of frames = {nframes-frames_start}')
        else:
            print(f'file already exists at {save_fpath}')
    cap.release()
    
    # check csv
    fdir, fname = get_dir_file_path(fpath)
    fname = change_extension(fname, 'csv')
    fpath_csv = os.path.join(fdir,fname)
    if os.path.isfile(fpath_csv):
        new_fname_csv = f'{basename}_eq.csv'
        save_fpath_csv = os.path.join(new_fdir,new_fname_csv)
        if not os.path.isfile(save_fpath) or overwrite == True:
            export_csv_rm_extra_lines(fpath_csv, fpath, new_path=save_fpath_csv)
            print(f'new csv saved at: {save_fpath_csv}\n')
        else:
            print(f'file already exists at {save_fpath_csv}')
    else:
        print('\nno .csv with the same filename found')
                
    

# test
# fdir = 'C:\\Users\\Fernando\\Desktop\\2cams movies -WT6dpf'
# fname = 'fish1_0.avi'
# fpath = os.path.join(fdir,fname)
# export_avi2tiff(fpath)


if __name__ == "__main__":
    fpath = sys.argv[1]
    if not os.path.isfile(fpath):
        sys.stdout(f'\nno file {fpath}')
        dirpath = fpath if os.path.isdir(fpath) == True else os.getcwd()
        fpath = file_menu(dirpath)
    export_avi2tiff(fpath)







#