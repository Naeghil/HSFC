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
        # TODO Might need to be different for glottis
        self.err = err  # Maximum accepted distance from a target
        self.targets = {}  # Known targets
        # TODO: this should be handled by the AST
        # Plan in terms of distance to cover and in what time
        self.plan = []  # Plan for current syllable production
        # TODO this should actually also hold the vowel, or at least be a coarticulated target?
        self.next = None # Next target in the plan as a label?


        print('Loading somatophoneme labels....')
        targets_raw = u.extractFileInfo('src/phono/targets')
        for i in range(int(len(targets_raw)/2)):
            self.targets[targets_raw[i*2]] = targets_raw[i*2+1]




    # TODO this actually adds a tuple ('target', activation)?
    def addNewTarget(self, t):
        self.plan.append(t)

    def __achieved(self, state):
        pass

    # Prediction the integral from 0 to T of the
    # interpolation of the velocities commands
    # TODO again this is a 1 parameter version
    def time(self, prediction, state):
        if abs(self.next[0]-state) < self.err:
            pass