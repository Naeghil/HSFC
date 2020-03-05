# -------------------------------------------------------------------------------
# Name:        main
# Purpose:     Main module of the application
#
# Author:      Naeghil
#
# Created:     15/02/2020
# Copyright:   (c) Naeghil 2020
# Licence:     <your licence>
# -------------------------------------------------------------------------------


import os
import sys
import ctypes

# Assumes src is in the same folder as main.py
# sys.path.append('./src/')
from src.utils.utils import extractFileInfo
from src.vtract.vtract import VocalTract
import src.test.test as test


def main():
    path = os.getcwd()
    while os.path.basename(path) != 'HSFC':
        path = os.path.normpath(path + os.sep + os.pardir)

    # Loading information from files:
    try:
        print('Loading configuration...')
        c_info = extractFileInfo(path + os.sep + 'config')
        if c_info is None:
            print('Loading configuration failed.')
            sys.exit()

        ext = '.dll' if sys.platform == 'win32' else '.so'
        conf = {'path': path,  # Path to the root of the application
                'apipath':  # Full path to the VTLAPI
                    path + c_info[1] + 'VocalTractLabApi' + c_info[0] + ext,
                'speaker':  # Full path to the speaker file
                    path + c_info[1] + c_info[2],
                'frate': int(c_info[3]),  # The frame rate
                'fsynth': int(c_info[4])}  # The synth rate

        print('Loading somatophoneme labels....')
        t_labels = extractFileInfo(
            path + os.sep + 'src' + os.sep + 'vtract' + os.sep + 'targets')
        if t_labels is None:
            print('Loading somatophoneme labels failed.')
            sys.exit()
    except Exception as e:
        print('Loading information from files failed: ', e)
        sys.exit()

    # Initializations:
    vt = None
    try:
        print('Initializing vocal tract...')
        vt = VocalTract(conf, False)

        print('Loading somatophoneme targets...')
        targets = {}
        tar_raw = extractFileInfo('src/phono/targets')
        for i in range(int(len(tar_raw)/2)):
            targets[tar_raw[2*i]] = \
                list(float(par) for par in tar_raw[2*i+1].split(' '))
    except Exception as e:
        print('Vocal Tract initialization failed: ', e)
        if vt:
            vt.close()
        sys.exit()

    # Tests
    try:
        # test.testDefault(vt)
        toTest = 'i'
        # test.testTargets(vt, targets[toTest], toTest)
    except Exception as e:
        print('Test failed: ', e)


    # Exit procedure:
    vt.close()


if __name__ == '__main__':
    main()