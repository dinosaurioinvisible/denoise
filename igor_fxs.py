

# first debug point: command in Igor Pro must be working to arrive here
# if anything fails immediatly after this, most probably is the imports
# also, importantly
# when run from igor pro, some normal python stuff throw errors, like:
# comments ending in : (like #something:)
# ask for indententation
# x = x if something or something2 else y
# complains because supposedly there's no else
# most of there can should be printed by the s_value in igor pro
# import pdb; pdb.set_trace()

import os
import sys
import subprocess
from platform import system
import tifffile as tf
import numpy as np
from ks_method import KS_pipeline

def test_fx(path_to_movie, debug=False):
    # just for testing
    if debug:
        # this saves in same python script folder
        if system() == 'Windows':
            subprocess.run("dir >> xtest.txt", shell=True)
            import pdb; pdb.set_trace()
        else:
            subprocess.run("ls -l >> xtest.txt", shell=True)
    # any imports/fxs you'd like to try go here
    #

if __name__ == "__main__":
    script = sys.argv[0]
    path_to_movie = sys.argv[1]
    deb = False
    for arg in sys.argv:
        deb = True if arg == '--debug' else deb
    if deb:
        test_fx(path_to_movie=path_to_movie, debug=deb)
    # here you can call any function
    # import pdb; pdb.set_trace()
    x = KS_pipeline(path_to_movie, debug=deb)



# string path_to_python_script = "C:\Users\Fernando\zf\denoise\igor_fxs.py"
# string path_to_movie = "C:\\Users\\Fernando\\Desktop\\Steps_pre_AF10_a1015.tif"





#
