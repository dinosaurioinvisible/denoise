
import os
import subprocess
from platform import system

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
    execute_command(f'PyIgorLoadWave({}, \"{}\", \"{wavename}\", \"{path}\", 0)')
