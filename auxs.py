
import os
import numpy as np

def file_menu(path='',file_ext=''):
    if path:
        try:
            os.chdir(path)
        except:
            print(f'\ncould\'t open: {path}')
    mistake = False
    while True:
        if mistake:
            print('\ninvalid option')
            mistake = False
        cwd = os.getcwd()
        print(f'\ncurrent location: {cwd}')
        print(f'current file extension: {file_ext}')
        entries = [i for i in os.listdir() if i.endswith(file_ext)]
        entries += [i for i in os.listdir() if os.path.isdir(i) and i not in entries]
        entries.sort()
        print()
        for ei,entry in enumerate(entries):
            print(f'{ei+1} - {entry}')
        print('[u] to go up a directory')
        print('[f] to change file extension')
        print('[q] to quit')
        xi = input("\n >> ")
        if xi == 'q' or xi == 'quit':
            return
        elif xi == 'f':
            file_ext = input('\nnew file extension >> ')
            print(f'new file ext: {file_ext}')
        elif xi == 'u' or xi == 'up':
            os.chdir('..')
        else:
            try:
                fname = entries[int(xi)-1]
                print(f'\nselected: {fname}')
            except:
                mistake = True
            if not mistake:
                if os.path.isdir(fname):
                    os.chdir(os.path.join(cwd,fname))
                else:
                    return fname

def deinterleave(stack):
    ch1 = stack[0::2]
    ch2 = stack[1::2]
    return ch1,ch2




























#
