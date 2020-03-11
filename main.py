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

# Assumes src is in the same folder as main.py
# sys.path.append('./src/')
from src.utils.utils import extractFileInfo
from src.vtract.vtract import VocalTract
from src.phono.SPT import SomatoPhonemeTargets
# from src.phono.MPP import MotorPhonemePrograms
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

        print('Loading somatophoneme targets...')
        spt = SomatoPhonemeTargets(0.0)

    except Exception as e:
        print('Loading information from files failed: ', e)
        sys.exit()

    # Initializations:
    vt = None
    try:
        print('Initializing vocal tract...')
        vt = VocalTract(conf, False)

    except Exception as e:
        print('Vocal Tract initialization failed: ', e)
        if vt:
            vt.close()
        sys.exit()

    t_labels = ['a', 'e', 'i', 'o', 'u', 'E:', 'A', 'I', 'E', 'O', 'U', '@6']
    u_labels = ['ll-labial-nas(u)', 'll-labial-stop(u)', 'll-labial-fric(u)', 'tt-alveolar-nas(u)',
                'tt-alveolar-stop(u)', 'tt-alveolar-lat(u)', 'tt-alveolar-fric(u)', 'tt-postalveolar-fric(u)',
                'tb-palatal-fric(u)', 'tb-velar-stop(u)', 'tb-velar-nas(u)']
    i_labels = ['ll-labial-nas(i)', 'll-labial-stop(i)', 'll-labial-fric(i)', 'tt-alveolar-nas(i)',
                'tt-alveolar-stop(i)', 'tt-alveolar-lat(i)', 'tt-alveolar-fric(i)', 'tt-postalveolar-fric(i)',
                'tb-palatal-fric(i)', 'tb-velar-stop(i)', 'tb-velar-nas(i)']
    a_labels = ['ll-labial-nas(a)', 'll-labial-stop(a)', 'll-labial-fric(a)', 'tt-alveolar-nas(a)',
                'tt-alveolar-stop(a)', 'tt-alveolar-lat(a)', 'tt-alveolar-fric(a)', 'tt-postalveolar-fric(a)',
                'tb-palatal-fric(a)', 'tb-velar-stop(a)', 'tb-velar-nas(a)']
    c_labels = ['ll-labial-nas', 'll-labial-stop', 'll-labial-fric', 'tt-alveolar-nas', 'tt-alveolar-stop',
                'tt-alveolar-lat', 'tt-alveolar-fric', 'tt-postalveolar-fric', 'tb-palatal-fric', 'tb-velar-stop', 'tb-velar-nas']






    # Tests
    # test.testDefault(vt)
    # i = 5
    # test.testTargets(vt, spt.targets[t_labels[i]], t_labels[i])


    # Exit procedure:
    # vt.close()


if __name__ == '__main__':
    main()
