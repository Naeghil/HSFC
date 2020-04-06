# -------------------------------------------------------------------------------
# Name:        Somato-Phonological Targets
# Purpose:     Module producing a correction signal depending on
#               current state and prediction
#
# Author:      Roberto Sautto
#
# Created:     04/03/2020
# Copyright:   (c) Roberto Sautto 2020
# Licence:     <your licence>
# -------------------------------------------------------------------------------

import src.utils.utils as u


class SomatoPhonemeTargets:
    def __init__(self, err):
        self.targets = {}  # Known targets
        self.vow_constants = {}
        self.con_constants = {}
        self.err = err

        # Targets as specified in VocalTractLabAPI and by Birkholz
        targets_raw = u.extractFileInfo('src/phono/targets')
        for i in range(int(len(targets_raw)/2)):
            self.targets[targets_raw[i*2]] = list(float(p) for p in targets_raw[i*2+1].split())

        parameters_raw = u.extractFileInfo('src/phono/targetpars')
        vow_const_raw = parameters_raw[0].split()
        con_const_raw = parameters_raw[1].split()
        # Constant times as specified by Birkholz
        for i in range(int(len(vow_const_raw)/2)):
            self.vow_constants[vow_const_raw[i*2]] = float(vow_const_raw[i*2+1])
        # Constant times as worked out in parameters testing
        for i in range(int(len(con_const_raw)/2)):
            self.vow_constants[con_const_raw[i*2]] = float(con_const_raw[i*2+1])
