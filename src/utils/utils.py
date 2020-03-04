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


def extractFileInfo(path):
    info = None
    with open(path) as i_file:
        # Extract non-blank lines
        info = (line.rstrip().lstrip() for line in i_file)  # no spaces
        info = (line for line in info if line)  # no empty lines
        info = list(line for line in info if line[0] != '#')  # no comments
    return info


class WorkingParametersList:
    labels = [] # Labels of the parameters for the synthesizer

    def __init__(self, vt_pars, g_pars, is_velocity=True):
        self.vt_pars = vt_pars  # Dictionary, change in vocal tract parameters
        self.g_pars = g_pars  # Dictionary, change in glottis parameters, adjusted:
        d = self.g_pars.pop('d_rest')
        self.g_pars['lower_rest_displacement'] = d
        self.g_pars['upper_rest_displacement'] = d
        # For testing purposes
        self.is_vel = is_velocity  # True: treated as velocities; else as new state


class SomatoTarget(WorkingParametersList):
    def __init__(self):
        WorkingParametersList.__init__(self, )
