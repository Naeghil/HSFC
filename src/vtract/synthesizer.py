# -------------------------------------------------------------------------------
# Name:        synthesizer
# Purpose:     Wrapper for the VocalTractLabAPI
#
# Author:      Roberto Sautto
#
# Created:     04/03/2020
# Copyright:   (c) Roberto Sautto 2020
# Licence:     <your licence>
# -------------------------------------------------------------------------------
import ctypes

import numpy as np
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
        self.audio_sampling_rate = TMPasr.value
        self.number_tube_sections = TMPtubenos.value
        self.vtp_no = TMPvtparno.value
        self.gp_no = TMPgloparno.value

    def getParametersInfo(self):
        print('  Retrieving parameters information...')
        return VTParametersInfo(self.api, self.vtp_no, self.gp_no)

    def display(self):
        print('    Audio sampling rate: ' + str(self.audio_sampling_rate))
        print('    Number of parameters vocal/glottis: ' + str(self.vtp_no) + '/' + str(self.gp_no))
        print('    Synthesis Frame Rate: ' + str(self.frame_rate) + 'Hz')

    def dump(self, newFrame):
        self.__vframes.extend(newFrame[0])
        self.__gframes.extend(newFrame[1])
        self.__noframes += 1

    # Empties the production frames and is ready to record a new utterance
    def flush(self):
        self.__gframes = []
        self.__vframes = []
        self.__noframes = 0

    # "to" included
    def __call__(self, start=0, to=None):
        if to is None:
            to = self.__noframes - start - 1

        # Parameters of the synthesis
        no_frames = to - start + 1
        duration_s = float(no_frames) / float(self.frame_rate)
        tube_areas = (ctypes.c_double * (no_frames * self.number_tube_sections))()
        tube_articulators = ctypes.c_char_p(b' ' * no_frames * self.number_tube_sections)
        number_audio_samples = ctypes.c_int(0)

        # init the arrays
        v_offset, v_end = (start * self.vtp_no,  to * self.vtp_no + 1)
        tract_params = (ctypes.c_double * (no_frames * self.vtp_no))(*(self.__vframes[v_offset:v_end]))
        g_offset, g_end = [start * self.gp_no, to * self.gp_no + 1]
        glottis_params = (ctypes.c_double * (no_frames * self.gp_no))(*self.__gframes[g_offset:g_end])
        audio = (ctypes.c_double * int(duration_s * self.audio_sampling_rate))()

        # Call the synthesis function. It may calculate a few seconds.
        failure = self.api.vtlSynthBlock(ctypes.byref(tract_params), ctypes.byref(glottis_params),  # inputs
                                         ctypes.byref(tube_areas), tube_articulators,  # outputs
                                         no_frames, ctypes.c_double(self.frame_rate),  # inputs
                                         ctypes.byref(audio), ctypes.byref(number_audio_samples))  # outputs
        if failure != 0: raise ValueError('Error in vtlSynthBlock! Errorcode: %i' % failure)

        wav = np.array(audio)
        return np.int16(wav * (2 ** 15 - 1))

    def close(self):
        if self.api: self.api.vtlClose()
