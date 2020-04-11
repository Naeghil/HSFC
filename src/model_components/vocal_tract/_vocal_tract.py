# -------------------------------------------------------------------------------
# Name:        vocal_tract
# Purpose:     Represents the vocal tract in HSFC, essentially holds the state
#              of the articulators at a given time, and uses the synthesizer
#
# Author:      Roberto Sautto
#
# Last mod:    8/04/2020
# Copyright:   (c) Roberto Sautto 2020
# Licence:     <your licence>
# -------------------------------------------------------------------------------

# Global imports
import numpy as np
# Local imports
from .. import _parameters_lists as PL
from ...utils import outputAudio
from ._parameters_information import getVocalLabels, getGlottalLabels, getWorkingLabels


class VocalTract:
    def __init__(self, synth, q_red, initial_state, audio_path="./"):
        self.__synth = synth  # The synthesizer
        # This provides some "quality reduction": only 1 in q_red states are "dumped" in the synthesizer
        # This is in order to speed up synthesis (see Report for more)
        self.__qred = q_red
        self.counter = 0  # Used to decide which states are dumped in the synthesizer
        # Current state, initialized as the neutral values:
        if isinstance(initial_state, dict):
            init_state = list(initial_state[k] for k in getVocalLabels()+getGlottalLabels())
        else:  # Any inaccuracy will be taken care of State._init()'s exceptions
            init_state = initial_state

        self.__state = PL.State(init_state)  # raises ValueError, unrecoverable

        self.__audiopath = audio_path  # Folder in which audio is output

    # Originally meant for to be used for time()
    def __updateState(self, vel):
        for k in getWorkingLabels():
            new = vel.get(k) + self.__state.get(k)
            self.__state.update(k, new)

    # Returns a copy of the current state for logging purposes
    def getState(self):
        return self.__state.asTargetParameters()

    # Advances "time" for the vocal tract, thus safely updating its state
    def time(self, new, labels=None):
        if labels is None:  # For testing purposes, labels can be provided to the function
            labels = getWorkingLabels()
        # Quality reduction
        if self.counter % self.__qred == 0:
            self.__synth.dump(self.__state.asFrame())  # Save the state as a frame
        self.counter += 1
        # State update
        for k in labels:
            # Defaults to the old parameter
            self.__state.update(k, new.get(k, self.__state.get(k)))

    # This function synthesizes the audio produced up to this moment
    # and clears the synthesizer
    def speak(self, label):
        utterance = np.array(self.__synth(), dtype=np.int16)
        self.__synth.flush()
        outputAudio(self.__audiopath, label, self.__synth.audio_sampling_rate, utterance)
        return utterance

    def close(self):
        # Needed because of the ctypes and internal states:
        if self.__synth: self.__synth.close()
