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
from src.orchestrator.orchestrator import Orchestrator
import src.test.test as test


def main(details=False):
    path = os.getcwd()
    while os.path.basename(path) != 'HSFC':
        path = os.path.normpath(path + os.sep + os.pardir)

    orch = Orchestrator(path, details)

    # t_labels = ['a', 'e', 'i', 'o', 'u', 'E:', 'A', 'I', 'E', 'O', 'U', '@6']


    ''' Simple Tests
    # vttest.testDefault(vt)
    # i = 5
    # vttest.testTargets(vt, spt.targets[t_labels[i]], t_labels[i]) '''
    ''' Syllable Test
    # vow = ['a', 'i', 'u']
    c_labels = ['m', 'b', 'v', 'n', 'd', 'N', 'l', 's', 'z', 'j\\', 'g']
    vi = 0
    ci = 1
    con = c_labels[ci] + vow[vi]
    test.testSyllable(vt, spt.targets['_'], spt.targets[vow[vi]], vow[vi], spt.targets[con], con) '''



if __name__ == '__main__':
    main()
