# -------------------------------------------------------------------------------
# Name:        utils
# Purpose:     Utility code
#
# Author:      Roberto Sautto
#
# Last mod:    8/04/2020
# Copyright:   (c) Roberto Sautto 2020
# Licence:     <your licence>
# -------------------------------------------------------------------------------

# Global imports
from scipy.io import wavfile
from datetime import datetime


# Exception utilities:
class UnrecoverableException(Exception):
    def __init__(self, message=''):
        super(UnrecoverableException, self).__init__(message)


class RecoverableException(Exception):
    def __init__(self, message=''):
        super(RecoverableException, self).__init__(message)


# Default method to extract information from HSFC's configuration and parameter files
def extractFileInfo(path):
    with open(path) as i_file:
        # Extract non-blank lines
        info = (line.rstrip().lstrip() for line in i_file)  # no spaces
        info = (line for line in info if line)  # no empty lines
        info = list(line for line in info if line[0] != '#')  # no comments
        return info


# Outputs audio to to file
def outputAudio(path, label, sampling_rate, audio):
    a_file = path + (label if label else 'audio') +\
             ' - ' + datetime.now().strftime("%d-%m-%Y-%H.%M.%S") + '.wav'
    wavfile.write(a_file, sampling_rate, audio)