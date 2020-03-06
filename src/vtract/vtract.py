# -------------------------------------------------------------------------------
# Name:        Vocal Tract
# Purpose:     Wrapper for VTLApi for the pruposes of this project
#
# Author:      Roberto Sautto
#
# Created:     13/02/2020
# Copyright:   (c) Roberto Sautto 2020
# Licence:     <your licence>
# Disclaimer:  Part of this code is adapted from "example1.py" from the
#              VocalTractLab API distribution v2.1b
# -------------------------------------------------------------------------------


import os
import copy
import numpy as np

from ..utils.utils import outputAudio
from ..vtract.synthesizer import Synthesizer
import src.utils.paramlists as pl

# 'pressure' string
p = 'pressure'


class VocalTract:
    # Construction (check the prints for details):
    def __init__(self, conf, details=True):
        # The synthesizer
        self.__synth = Synthesizer(conf['apipath'], conf['speaker'], conf['frate'])
        # States synthesized together
        self.__fsynth = conf['fsynth']
        # The parameters for the synthesizer
        self.parameters = self.__synth.getParametersInfo()  # Parameters of the synthesizer
        self.__state = {}  # Current state
        self.__next_frame = 0  # Next frame to synthesize

        self.__audio = np.empty(0, np.int16)  # Generated audio
        # Folder in which audio is output:
        # TODO: this doesn't work
        self.__audiopath = conf['path'] + os.sep + 'Output' + os.sep

        if details: self.__synth.display()
        if details: self.parameters.display()
        print('  Initializing the vocal tract state...')  # as the neutral values
        self.__state = pl.State(copy.deepcopy(self.parameters.getDefaults()))
        if details: self.display()

    # TODO this is for test purposes
    def getApi(self):
        return self.__synth.api

    def display(self):
        print(self.__state.asString())

    # TODO check if deepcopy is actually needed
    # Returns a copy of the current state
    def getState(self):
        return copy.deepcopy(self.__state)

    # In a perfect world, this would return orosensory information, but I'm not sure how to do that
    # TODO: calculate "strain" (?) from current position and natural position
    def __updateState(self, in_par):
        for k in in_par.working_labels:
            new = in_par.get(k) + (self.__state.get(k))
            self.__state.update(k, self.parameters.validate(k, new))

    def time(self, t, vtin=None, partialSynth=True):
        self.__synth.dump(self.__state.asFrame())  # Save the current state as a frame
        f_left = t - self.__next_frame + 1
        if partialSynth and (f_left >= self.__fsynth):
            self.__synth(self.__next_frame, t)
            self.__next_frame = t+1
        if vtin:
            self.__updateState(vtin)

    def close(self, t=None, label=None):
        # Produce the overall audio output before closing:
        if t and t-self.__next_frame is not 0:
            self.__audio = np.append(self.__audio, self.__synth(self.__next_frame, t))
            outputAudio(self.__audiopath, label, self.__synth.audio_sampling_rate, self.__audio)
        # Needed because of the ctypes and internal states:
        if self.__synth: self.__synth.close()
