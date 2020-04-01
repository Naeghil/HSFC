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

        targets_raw = u.extractFileInfo('src/phono/targets')
        for i in range(int(len(targets_raw)/2)):
            self.targets[targets_raw[i*2]] = list(float(p) for p in targets_raw[i*2+1].split())

