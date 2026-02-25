# -*- coding: utf-8 -*-

'''
To call animation functions from terminal
'''

import os
import sys
from utils.loading import file_menu
import numpy as np
import tifffile as tf 
from utils import plotting_fxs


def play_movie(fpath, 
               title='u',
               step=10):
    movie = tf.imread(fpath)
    # plotting_fxs.tensor_animation(movie, step=step)
    plotting_fxs.tensor_animation_pausable(movie, step=step)
    # plotting_fxs.tensor_animation_subplots(movie, step=step)

if __name__ == "__main__":
    fpath = ''
    step = 10
    args = sys.argv[1:]
    if len(args) > 0:
        for arg in args:
            if os.path.isfile(arg):
                fpath = arg
            if arg == '--step' or arg == '-s':
                step_index = [i for i,x in enumerate(args) if x == '--step' or x == '-s'][0] + 1
                step = args[step_index]
    if not os.path.isfile(fpath):
        print('\nno filepath found')
        dirpath = fpath if os.path.isdir(fpath) == True else os.getcwd()
        fpath = file_menu(dirpath)
    play_movie(fpath, step=step)
