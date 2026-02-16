# -*- coding: utf-8 -*-

import os, sys
import cv2
from tqdm import tqdm
from auxs import change_extension, get_dir_file_path
from loading import file_menu
import tifffile as tf
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

def export_avi2tiff(fpath):
    fdir,fname = get_dir_file_path(fpath)    
    cap = cv2.VideoCapture(fpath)
    size = 6000
    nframes = 0
    basename = change_extension(fname,'')
    new_fdir = os.path.join(fdir,basename)
    if not os.path.isdir(new_fdir):
        os.mkdir(new_fdir)
    keep = True
    while keep:
        frames = []
        frames_start = nframes
        nframes_end = count_avi_frames(fpath)
        nframes_end = min(nframes+size,nframes_end)
        for _ in tqdm(range(nframes,nframes_end)):  
            ret, frame = cap.read()
            if not ret:
                keep = False
                break
            frame_gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            frames.append(frame_gray)
            nframes += 1
        farray = np.array(frames)
        
        keep = False if nframes >= nframes_end else keep
        # import pdb; pdb.set_trace()
        new_fname = f'{basename}_{frames_start}-{nframes}.tiff'
        save_fpath = os.path.join(new_fdir,new_fname)
        tf.imwrite(save_fpath, farray)
        print(f'file saved at {save_fpath} - number of frames = {nframes-frames_start}')
    cap.release()

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