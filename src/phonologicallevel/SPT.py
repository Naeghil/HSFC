# -------------------------------------------------------------------------------
# Name:        Somato-Phonological Targets
# Purpose:     Originally meant as a feedback module, it now serves the purpose of
#              "knowing" things about the parameters for each phoneme.
#              It is essentially a data bag.
#
# Author:      Roberto Sautto
#
# Created:     04/03/2020
# Copyright:   (c) Roberto Sautto 2020
# Licence:     <your licence>
# -------------------------------------------------------------------------------

# Local imports
import src.utils.utils as u


class SomatoPhonemeTargets:
    def __init__(self, err):
        self.targets = {}  # Known targets
        self.vow_constants = {}  # Known constant times for vowels
        self.con_constants = {}  # Known constant times for consonants
        self.err = err  # Known maximum achievable error

        # Targets as specified in VocalTractLabAPI and by Birkholz (see Report)
        targets_raw = u.extractFileInfo('src/phonologicallevel/targets')  # raises FileNotFound, unrecoverable
        for i in range(int(len(targets_raw)/2)):
            self.targets[targets_raw[i*2]] = list(float(p) for p in targets_raw[i*2+1].split())

        # Time constants (see targetpars file)
        parameters_raw = u.extractFileInfo('src/phonologicallevel/targetpars')  # raises FileNotFound, unrecoverable
        vow_const_raw = parameters_raw[0].split()
        con_const_raw = parameters_raw[1].split()
        # Constant times as specified by Birkholz
        for i in range(int(len(vow_const_raw)/2)):
            self.vow_constants[vow_const_raw[i*2]] = float(vow_const_raw[i*2+1])
        # Constant times as worked out in parameters testing
        for i in range(int(len(con_const_raw)/2)):
            self.vow_constants[con_const_raw[i*2]] = float(con_const_raw[i*2+1])
