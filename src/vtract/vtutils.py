# -------------------------------------------------------------------------------
# Name:        vtutils
# Purpose:     Some utility classes for the vocal tract module
#
# Author:      Roberto Sautto
#
# Created:     14/02/2020
# Copyright:   (c) Roberto Sautto 2020
# Licence:     <your licence>
# -------------------------------------------------------------------------------

import ctypes
from scipy.io import wavfile
from datetime import datetime
from src.utils.utils import WorkingParametersList



# This class contains utility functions for the vocal tract
class vtu:
    def __init__(self):
        pass

    @staticmethod
    def outputAudio(path, label, sampling_rate, audio):
        a_file = 'audio' + ((' - '+label) if label else '') +\
                 ' - ' + datetime.now().strftime("%d-%m-%Y-%H.%M.%S") + '.wav'
        wavfile.write(a_file, sampling_rate, audio)




# Mainly a data container to avoid passing glottis parameters everytime
class VTInput(WorkingParametersList):
    pass