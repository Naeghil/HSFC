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
import time

import numpy as np

from src.utils.utils import outputAudio
import src.utils.paramlists as pl
from src.vtract.paraminfo import VTParametersInfo as PI


class VocalTract:
    # Construction (check the prints for details):
    def __init__(self, synth, q_red, initial_state, audio_path="./"):
        self.__synth = synth  # The synthesizer
        self.__qred = q_red  # Only 1 in q_red states are actually "dumped" in the synthesizer
        init_state = list(initial_state[k] for k in PI.vlabels+PI.glabels)
        self.__state = pl.State(init_state)  # Current state, initialized as the neutral values
        self.__next_frame = 0  # Next frame to synthesize
        self.__audio = np.empty(0, np.int16)  # Generated audio
        self.__audiopath = audio_path  # Folder in which audio is output
        self.counter = 0  # Used to decide which states are dumped in the synthesizer

    # In a perfect world, this would return orosensory information, but I'm not sure how to do that
    def __updateState(self, vel):
        for k in PI.working_labels:
            new = vel.get(k) + (self.__state.get(k))
            self.__state.update(k, new)

    # Returns a copy of the current state
    def getState(self):
        return self.__state.asTargetParameters()

    # Trajectory-based alternative for the time() function
    def setState(self, new):
        if self.counter % self.__qred == 0:
            self.__synth.dump(self.__state.asFrame())
        self.counter += 1
        for k in PI.working_labels:
            self.__state.update(k, new.get(k))

    # Advances the "time" thus updating the state depending on the current velocity
    def time(self, vtin=None):
        if self.counter % self.__qred == 0:
            self.__synth.dump(self.__state.asFrame())  # Save the current state as a frame
        if vtin:
            self.__updateState(vtin)

    # This function synthesizes the audio produced up to this moment
    # and clears the synthesizer
    def speak(self, label):
        t0 = time.time()
        utterance = np.array(self.__synth(), dtype=np.int16)
        t1 = time.time()
        dt = str(int(t1-t0))+' - '
        self.__synth.flush()
        outputAudio(self.__audiopath, dt+label, self.__synth.audio_sampling_rate, utterance)
        return utterance

    def close(self):
        # Needed because of the ctypes and internal states:
        if self.__synth: self.__synth.close()
