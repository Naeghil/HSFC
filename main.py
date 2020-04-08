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

# Assumes src is in the same folder as main.py
from queue import Queue

from src.orchestrator.orchestrator import Orchestrator
import src.test.test as test


def main(details=False):
    # Obtains the root path to the sourcecode, independently from where in the code it's starting
    # BUG: it doesn't work if it's from outside the root directory of the code
    path = os.getcwd()
    while os.path.basename(path) != 'HSFC':
        path = os.path.normpath(path + os.sep + os.pardir)

    # Creates queue for user commands
    toSay = Queue(0)
    # Creates bucket for orchestrator's message passing
    bucket = Queue(0)
    # Creates the orchestrator
    orch = Orchestrator(path, details, toSay, bucket)  # raises Exception, unrecoverable

    # t_labels = ['a', 'e', 'i', 'o', 'u', 'E:', 'A', 'I', 'E', 'O', 'U', '@6']

    vow = ['a', 'i', 'u']
    ''' Simple Tests
    # vttest.testDefault(vt)
    # i = 5
    # vttest.testTargets(vt, spt.targets[t_labels[i]], t_labels[i]) '''
    ''' Syllable Test
    c_labels = ['m', 'b', 'v', 'n', 'd', 'l', 'z', 'j\\', 'g']
    vi = 0
    ci = 1
    con = c_labels[ci] + vow[vi]
    test.testSyllable(vt, spt.targets['_'], spt.targets[vow[vi]], vow[vi], spt.targets[con], con)

    c_graphemes = ['m', 'b', 'v', 'n', 'd', 'l', 'z', 'gli', 'g']
    v = 0
    for c in c_graphemes:
        for v in vow:
            test.testMSP(orch, c+v)
            test.testMSP(orch, c+v+c+v)
    

    sel_syllables = ['ga', 'ba', 'da', 'di', 'za', 'zi', 'zu', 'glia', 'gli', 'gliu', 'ma',
                     'mi', 'mu', 'na', 'ni', 'nu', 'la', 'li', 'lu', 'va', 'vi', 'vu']

    for syllablelevel in sel_syllables:
        test.testMSP(orch, syllablelevel)
        test.testMSP(orch, syllablelevel+syllablelevel) '''

    orch.terminate()


if __name__ == '__main__':
    main()
