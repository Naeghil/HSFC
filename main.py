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
import src.utils.init_utils as init
import src.vtract.expose as vtract

import src.utils.paramlists as PL
from src.phono.SPT import SomatoPhonemeTargets
# from src.phono.MPP import MotorPhonemePrograms
import src.test.test as test


def main():
    details = False

    path = os.getcwd()
    while os.path.basename(path) != 'HSFC':
        path = os.path.normpath(path + os.sep + os.pardir)

    # Initializing system-wide configurations:
    try:
        print('Loading configuration...')
        conf = init.loadConfig()
        # Even though this is not a configuration,
        # the api requires to be initialized before
        # parameters information can be extracted
        print('Initializing syntesizer...')
        synthesizer = vtract.Synthesizer(conf['apipath'], conf['speaker'], conf['frate'])
        if details: synthesizer.display()
        print('Loading parameters information...')
        param_info = synthesizer.getParametersInfo()
        if details: param_info.display()
        print('Initializing parameters list indexing...')
        # Using parameters info to set up the paramlist indexing method
        PL.ParList.setIndexes(param_info.vlabels+param_info.glabels, param_info.working_labels)

        print('Loading somatophoneme targets...')
        spt = SomatoPhonemeTargets(0.0)

    except Exception as e:
        print('Loading configuration failed: ', e)
        sys.exit()

    # Initializations:
    vt = None
    try:
        print('Initializing vocal tract...')
        audiopath = conf['path'] + os.sep + 'Output' + os.sep
        vt = vtract.VocalTract(synthesizer, conf['fsynth'], param_info.getDefaults(), param_info.validate, audiopath)

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
    c_labels = ['ll-labial-nas', 'll-labial-stop', 'll-labial-fric', 'tt-alveolar-nas', 'tt-alveolar-stop', 'tb-velar-nas',
                'tt-alveolar-lat', 'tt-alveolar-fric', 'tt-postalveolar-fric', 'tb-palatal-fric', 'tb-velar-stop']
    # Voiced/Voiceless?
    actual_consonants = ['m', 'b', 'v', 'n', 'd', 'gn', 'l', 's', 'gi', 'sh?', 'g']

    # Tests
    # test.testDefault(vt)
    # i = 5
    # test.testTargets(vt, spt.targets[t_labels[i]], t_labels[i])
    vow = ['a', 'i', 'u']
    vi = 1
    ci = 0
    con = c_labels[ci] + '(' + vow[vi] + ')'
    test.testSyllable(vt, spt.targets[vow[vi]], vow[vi], spt.targets[con], con)

    # Exit procedure:
    # vt.close()


if __name__ == '__main__':
    main()
