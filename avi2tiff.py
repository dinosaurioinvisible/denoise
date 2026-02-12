# -*- coding: utf-8 -*-

import os
import cv2
from tqdm import tqdm
from auxs import change_extension, get_dir_file_paths
import tifffile as tf
import numpy as np


def avi2tiff(fpath):
    fdir,fname = get_dir_file_paths(fpath)
    
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
        
        for _ in tqdm(range(nframes,nframes+size)):  
            ret, frame = cap.read()
            if not ret:
                keep = False
                break
            frame_gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            frames.append(frame_gray)
            nframes += 1
        
        farray = np.array(frames)
        
        new_fname = f'{basename}_{frames_start}-{nframes}.tiff'
        save_fpath = os.path.join(new_fdir,new_fname)
        tf.imwrite(save_fpath, farray)
        print(f'file saved at {save_fpath} - number of frames = {nframes-frames_start}')
    
    cap.release()
    

# test
fdir = 'C:\\Users\\Fernando\\Desktop\\2cams movies -WT6dpf'
fname = 'fish1_0.avi'
fpath = os.path.join(fdir,fname)
avi2tiff(fpath)









#