# -------------------------------------------------------------------------------
# Name:        init_utils
# Purpose:     utility functions to declutter main.main()
#
# Author:      Roberto Sautto
#
# Created:     05/03/2020
# Copyright:   (c) Roberto Sautto 2020
# Licence:     <your licence>
# -------------------------------------------------------------------------------

import os
import sys
from src.utils.utils import extractFileInfo


def localPath():
    path = os.getcwd()
    while os.path.basename(path) != 'HSFC':
        path = os.path.normpath(path + os.sep + os.pardir)
    return path


def loadConfig(path):
    c_info = extractFileInfo(path+os.sep+'config')
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
    return conf
