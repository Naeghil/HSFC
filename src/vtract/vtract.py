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


import numpy as np

from src.utils.utils import outputAudio
import src.utils.paramlists as pl

# 'pressure' string
p = 'pressure'


class VocalTract:
    # Construction (check the prints for details):
    def __init__(self, synth, f_synth, initial_state, audio_path="./"):
        self.__synth = synth  # The synthesizer
        self.__fsynth = f_synth  # States synthesized together
        self.__state = pl.State(initial_state)  # Current state, initialized as the neutral values
        self.__next_frame = 0  # Next frame to synthesize
        self.__audio = np.empty(0, np.int16)  # Generated audio
        self.__audiopath = audio_path  # Folder in which audio is output

    # TODO this is for test purposes
    def getApi(self):
        return self.__synth.api

    def display(self):
        print(self.__state.asString())

    # Returns a copy of the current state
    def getState(self):
        return self.__state

    # TODO: for test purposes
    def setState(self, new):
        self.__synth.dump(self.__state.asFrame())
        for k in new.working_labels:
            self.__state.update(k, new.get(k))

    # In a perfect world, this would return orosensory information, but I'm not sure how to do that
    # TODO: calculate "strain" (?) from current position and natural position
    def __updateState(self, vel):
        for k in vel.working_labels:
            new = vel.get(k) + (self.__state.get(k))
            self.__state.update(k, new)

    def time(self, t, vtin=None, partialSynth=True):
        self.__synth.dump(self.__state.asFrame())  # Save the current state as a frame
        f_left = t - self.__next_frame + 1
        if partialSynth and (f_left >= self.__fsynth):
            self.__synth(self.__next_frame, t)
            self.__next_frame = t + 1
        if vtin:
            self.__updateState(vtin)

    def close(self, t=None, label=None):
        # Produce the overall audio output before closing:
        if t and t - self.__next_frame is not 0:
            self.__audio = np.append(self.__audio, self.__synth(self.__next_frame, t))
            outputAudio(self.__audiopath, label, self.__synth.audio_sampling_rate, self.__audio)
        # Needed because of the ctypes and internal states:
        if self.__synth: self.__synth.close()
