
import os
import sys
import subprocess
from platform import system
import tifffile as tf
import numpy as np
from ks_method import KS_pipeline

'''
1. call from igor
2. open with / put into igor
3. put script in user procedures
4. make button in igor
5. generalize to more scripts
'''

def execute_command(command, exec_path):
    if system() == 'Windows':
        temp = subprocess.list2cmdline([exec_path, "-Q", "-X"])
        subprocess.run(f'{temp} {command}')
    else:
        subprocess.run(exec_path, "-Q", "-X", command)

def convert_to_igor_path(path):
    return path.replace(os.path.sep, ":")

def put(self, wave, wavename, path, x0=0, dx=1):
    with h5py.File(path, "w") as f:
        dataset = f.create_dataset(uid, data=wave)
    # execute_command(f'PyIgorLoadWave({}, \"{wavename}\", \"{path}\", 0)')

def test_fx(path_to_movie, debug=False):
    # just for testing
    if debug:
        if system() == 'Windows':
            subprocess.run("dir >> xtest.txt", shell=True)
            import pdb; pdb.set_trace()
        else:
            subprocess.run("ls -l >> xtest.txt", shell=True)
    movie_raw = tf.imread(path_to_movie)
    movie_deint = movie_raw[0::2]
    savepath = ''.join(path_to_movie.split('.')[:-1])+'_xtest2.tiff'
    tf.imwrite(savepath, movie_deint)
    igor_save_path = convert_to_igor_path(savepath)
    # return igor_save_path


if __name__ == "__main__":
    script = sys.argv[0]
    path_to_movie = sys.argv[1]
    debug = True
    for arg in sys.argv:
        debug = True if arg == '--debug' or arg == '-d' else debug
    if debug:
        test_fx(path_to_movie=path_to_movie, debug=debug)
        import pdb; pdb.set_trace()
    # here you can call any other function
    x = KS_pipeline(path_to_movie, debug=debug)




# string path_to_python_script = "C:\Users\Fernando\zf\denoise\igor_fxs.py"
# string path_to_movie = "C:\\Users\\Fernando\\Desktop\\Steps_pre_AF10_a1015.tif"





#
