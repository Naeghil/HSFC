# -------------------------------------------------------------------------------
# Name:        synthesizer
# Purpose:     Wrapper for the VocalTractLabAPI.
#
# Author:      Roberto Sautto
#
# Last mod:    08/04/2020
# Copyright:   (c) Roberto Sautto 2020
# Licence:     <your licence>
# Disclaimer:  Part of this code is adapted from "example1.py" from the
#              VocalTractLab API distribution v2.1b
# -------------------------------------------------------------------------------

# Global imports
import ctypes
import numpy as np
# Local imports
from src.vtract.paraminfo import VTParametersInfo


class Synthesizer:
    # Construction (check the prints for details):
    def __init__(self, apipath, speaker, f_rate, q_red):
        print('  Loading VocalTractLabApi binary...')
        self.api = ctypes.cdll.LoadLibrary(apipath)
        # Parameters of the synthesizer
        self.audio_sampling_rate = 0  # Of the synthesizer
        self.number_tube_sections = 0  # Of the articulatory model
        self.vtp_no = 0  # Number of VT parameters
        self.gp_no = 0  # Number of glottis parameters
        self.frame_rate = int(f_rate/q_red)  # Synthesized frames per second of audio
        # Frames to be synthesized:
        self.__gframes = []  # Past (glottal) states ready to synthesize
        self.__vframes = []  # Past (vocal) states ready to syntheisze
        self.__noframes = 0  # Number of currently stored frames

        print('  Initializing the synthesizer...')
        if self.api.vtlInitialize(ctypes.c_char_p(speaker.encode())) != 0:
            raise ValueError('Error in vtlInitialize!')
        print('  Retrieving constants...')
        # Temporary variables to store the constants so I can get rid of the ctypes
        TMPasr, TMPtubenos, TMPvtparno, TMPgloparno = \
            (ctypes.c_int(0), ctypes.c_int(0), ctypes.c_int(0), ctypes.c_int(0))
        self.api.vtlGetConstants(ctypes.byref(TMPasr),
                                 ctypes.byref(TMPtubenos),
                                 ctypes.byref(TMPvtparno),
                                 ctypes.byref(TMPgloparno))
        # Save the parameters
        self.audio_sampling_rate = TMPasr.value
        self.number_tube_sections = TMPtubenos.value
        self.vtp_no = TMPvtparno.value
        self.gp_no = TMPgloparno.value

    # Returns a VTParametersInfo object, stored in the orchestrator
    def getParametersInfo(self):
        print('  Retrieving parameters information...')
        return VTParametersInfo(self.api, self.vtp_no, self.gp_no)

    # Displays information to the user
    def display(self):
        print('    Audio sampling rate: ' + str(self.audio_sampling_rate))
        print('    Number of parameters vocal/glottis: ' + str(self.vtp_no) + '/' + str(self.gp_no))
        print('    Synthesis Frame Rate: ' + str(self.frame_rate) + 'Hz')

    # Recevies an array containing the vocal tract and glottal frames, used in the synthesis
    def dump(self, newFrame):
        self.__vframes.extend(newFrame[0])
        self.__gframes.extend(newFrame[1])
        self.__noframes += 1

    # Empties the production frames and is ready to record a new utterance
    def flush(self):
        self.__gframes = []
        self.__vframes = []
        self.__noframes = 0

    # Synthesize the audio from the stored frames
    def __call__(self):
        # Parameters of the synthesis
        duration_s = float(self.__noframes) / float(self.frame_rate)
        tube_areas = (ctypes.c_double * (self.__noframes * self.number_tube_sections))()
        tube_articulators = ctypes.c_char_p(b' ' * self.__noframes * self.number_tube_sections)
        number_audio_samples = ctypes.c_int(0)

        # init the arrays
        v_offset, v_end = (0,  (self.__noframes-1) * self.vtp_no + 1)
        tract_params = (ctypes.c_double * (self.__noframes * self.vtp_no))(*(self.__vframes[v_offset:v_end]))
        g_offset, g_end = [0, (self.__noframes-1) * self.gp_no + 1]
        glottis_params = (ctypes.c_double * (self.__noframes * self.gp_no))(*self.__gframes[g_offset:g_end])
        audio = (ctypes.c_double * int(duration_s * self.audio_sampling_rate))()

        # Call the synthesis function. It may calculate a few seconds.
        failure = self.api.vtlSynthBlock(ctypes.byref(tract_params), ctypes.byref(glottis_params),  # inputs
                                         ctypes.byref(tube_areas), tube_articulators,  # outputs
                                         self.__noframes, ctypes.c_double(self.frame_rate),  # inputs
                                         ctypes.byref(audio), ctypes.byref(number_audio_samples))  # outputs
        if failure != 0: raise ValueError('Error in vtlSynthBlock! Errorcode: %i' % failure)

        wav = np.array(audio)
        return np.int16(wav * (2 ** 15 - 1))

    def close(self):
        if self.api: self.api.vtlClose()
