
import os
import sys
import subprocess
from platform import system
import tifffile as tf
import numpy as np

def execute_command(command, exec_path):
    if system() == 'Windows':
        temp = subprocess.list2cmdline([exec_path, "-Q", "-X"])
        subprocess.run(f'{temp} {command}')
    else:
        subprocess.run(exec_path, "-Q", "-X", command)

def convert_to_igor_path(path):
    return path.replace(os.path.sep, ":")

def get(self, wavename):
    return

def put(self, wave, wavename, path, x0=0, dx=1):
    with h5py.File(path, "w") as f:
        dataset = f.create_dataset(uid, data=wave)
    # execute_command(f'PyIgorLoadWave({}, \"{wavename}\", \"{path}\", 0)')

def test_fx(path_to_script, path_to_movie):
    # just for testing
    # subprocess.run("dir >> test.txt", shell=True)
    # import pdb; pdb.set_trace()
    movie_raw = tf.imread(path_to_movie)
    movie_deint = movie_raw[0::2]
    savepath = ''.join(path_to_movie.split('.')[:-1])+'_deint.tiff'
    # tf.imwrite(fpath_save, movie_deint)
    igor_save_path = convert_to_igor_path(savepath)



    # return igor_save_path

# test_fx()
if __name__ == "__main__":
    script = sys.argv[0]
    movie = sys.argv[1]
    test_fx(path_to_script=script, path_to_movie=movie)











#
