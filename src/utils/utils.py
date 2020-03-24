# -------------------------------------------------------------------------------
# Name:        utils
# Purpose:     defines utilities to be used throughout the program
#
# Author:      Roberto Sautto
#
# Created:     18/02/2020
# Copyright:   (c) Roberto Sautto 2020
# Licence:     <your licence>
# -------------------------------------------------------------------------------

from scipy.io import wavfile
from datetime import datetime


def extractFileInfo(path):
    with open(path) as i_file:
        # Extract non-blank lines
        info = (line.rstrip().lstrip() for line in i_file)  # no spaces
        info = (line for line in info if line)  # no empty lines
        info = list(line for line in info if line[0] != '#')  # no comments
        return info


def outputAudio(path, label, sampling_rate, audio):
    a_file = path + 'audio' + ((' - '+label) if label else '') +\
             ' - ' + datetime.now().strftime("%d-%m-%Y-%H.%M.%S") + '.wav'
    wavfile.write(a_file, sampling_rate, audio)
