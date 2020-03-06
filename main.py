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
from src.utils.utils import extractFileInfo
from src.vtract.vtract import VocalTract
from src.phono.SPT import SomatoPhonemeTargets
import src.utils.init_utils as init
import src.test.test as test


def main():
    # Pre-initialization
    try:
        path = init.localPath()
        print('Loading configuration...')
        conf = init.loadConfig(path)
    except Exception as e:
        tb = sys.exc_info()[2]
        print('Loading configuration from files failed: ', e.with_traceback(tb))
        sys.exit()

    # Initializations:
    vt = None
    try:
        print('Initializing vocal tract...')
        vt = VocalTract(conf, False)
        print('Initializing phonological level...')
        spt = SomatoPhonemeTargets(conf['err'])

    except Exception as e:
        tb = sys.exc_info()[2]
        print('Initialization failed: ', e.with_traceback(tb))
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
