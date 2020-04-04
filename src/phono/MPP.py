# -------------------------------------------------------------------------------
# Name:        Motor-Phoneme Programs
# Purpose:     Module producing a correction signal depending on
#               current state and prediction
#
# Author:      Roberto Sautto
#
# Created:     04/03/2020
# Copyright:   (c) Roberto Sautto 2020
# Licence:     <your licence>
# -------------------------------------------------------------------------------
import copy

import numpy as np

import src.phono.motcommand as mc
from src.utils.paramlists import Target


class BirkholzMotorControl:
    def __init__(self, i_state, frate=1000.0):
        self.__plan = []
        self.__progression = -1  # Index of the current command
        self.__dt = 1000.0/frate  # dt is in ms
        self.__max_error = 0.04  # TODO: maybe pass this to the constructor or is it command-dependent?
        # Initialize the command as a "static" command, by using the initial state as target
        initial_dstate = \
            np.array(list(i_state) + [0.0] * len(i_state) * (mc.MotorCommand.N-1), dtype='f8')\
                .reshape(mc.MotorCommand.N, len(i_state))
        self.__command = mc.MotorCommand(Target(10.0, i_state), initial_dstate, self.__dt)

    # This calculates the error as MSQ
    # TODO: consider different kinds of errors, e.g. percentage
    def __error(self, state):
        return np.square(state - self.__command.target).mean()

    # Advances to the next command in the plan, if available
    # Returns True if the plan has been executed fully, false if there's steps left
    def __advance(self):
        if self.__progression < len(self.__plan) - 1:
            self.__progression += 1
            self.__command = mc.MotorCommand(self.__plan[self.__progression],
                                             self.__command.getFinalValues(), self.__dt)
            return False
        return True

    def addPlan(self, targets):
        self.__plan += targets
        self.__advance()

    def getCurrentTarget(self):
        return copy.deepcopy(self.__command.target)

    # This function moves the command along as trajectories
    # i.e. calculates the 0th derivative of the system
    def ttime(self, state):
        end = False
        if self.__error(state) < self.__max_error:
            end = self.__advance()
        return end, self.__command.y()

    # This function moves the command along by calculating instantaneous acceleration
    def time(self, state):
        end = False
        if self.__error(state) < self.__max_error:
            end = self.__advance()
        acc = self.__command.time()
        return end, acc


# This is here because there were meant to be multiple kinds of MPP:
MotorPhonemePrograms = BirkholzMotorControl
