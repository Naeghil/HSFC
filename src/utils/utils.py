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

import matplotlib.pyplot as pl
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
    a_file = path + (label if label else 'audio') +\
             ' - ' + datetime.now().strftime("%d-%m-%Y-%H.%M.%S") + '.wav'
    wavfile.write(a_file, sampling_rate, audio)


class plot:
    @staticmethod
    def plot_all(data, tars, tar_cols, x_max):
        # Initial/Final: black
        # Consonant: green
        # Vowel: red
        fig = pl.figure()
        par_no = data.shape[0]
        for i in range(par_no):
            sf = fig.add_subplot(6, 4, i+1)
            sf.plot(data[i])
            for idx in range(len(tars)):
                sf.plot([tars[idx][i]] * x_max, tar_cols[idx])
        pl.subplots_adjust(hspace=1.0)
        pl.show()

    @staticmethod
    def plot(data, tars, tar_cols, x_max):
        # Initial/Final: black
        # Consonant: green
        # Phonation blue
        # Vowel: red
        pl.plot(data)
        for idx in range(len(tars)):
            pl.plot([tars[idx]] * x_max, tar_cols[idx])
        pl.show()
