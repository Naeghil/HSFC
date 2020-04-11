# -------------------------------------------------------------------------------
# Name:        MPP
# Purpose:     Originally meant as a subcomponent of HSFC, it provides similar
#              functionalities, handling the succession and execution of motor
#              commands at the phoneme level (i.e. phoneme by phoneme)
#
# Author:      Roberto Sautto
#
# Last mod:    07/04/2020
# Copyright:   (c) Roberto Sautto 2020
# Licence:     <your licence>
# -------------------------------------------------------------------------------

# Global imports
import numpy as np
# Local imports
from ._motor_command import MotorCommand
from .._parameters_lists import Target


class MotorPhonemePrograms:
    _expected_target = None  # This function "sanitizes" possibly unreachable targets
    # for the purpose of judging when it's time to move on, set from _parameters_information.py

    def __init__(self, initial_state, frate=1000.0, err=0.04):
        self.__plan = []
        self.__progression = -1  # Index of the current command
        self.__dt = 1000.0/frate  # time increment is in ms (see MotorCommand)
        self.__max_error = err  # Maximum achievable error:
        # if the distance from the target is less than this number, the plan advances

        # Initialize the command as a "static" command, by using the initial state as target
        len_is = len(initial_state)
        initial_dstate = np.array(list(initial_state) + [0.0] * len_is * (MotorCommand.N-1), dtype='f8'
                                  ).reshape(MotorCommand.N, len_is)
        # "Static" command, which means the MPP simply doesn't move the articulators
        self.__command = MotorCommand(Target(10.0, initial_state),  # raises UnrecoverableException
                                      initial_dstate, self.__dt)  # raises UnrecoverableException
        self.__current_expected_target = MotorPhonemePrograms._expected_target(self.__command.target)

    # Calculates the distance from the expected target as Mean Square Error
    def __error(self, state):
        return (np.square(state - self.__current_expected_target)).mean()

    # Advances to the next command in the plan, if available
    # Returns True if the plan has been executed, False if there's steps left
    def __advance(self):
        if self.__progression < len(self.__plan) - 1:
            self.__progression += 1
            self.__command = MotorCommand(self.__plan[self.__progression],
                                          self.__command.getFinalValues(),
                                          self.__dt)  # raises UnrecoverableException
            self.__current_expected_target = MotorPhonemePrograms._expected_target(self.__command.target)
            return False
        return True

    @staticmethod
    def setSanitizingFunction(function):
        if MotorPhonemePrograms._expected_target is None:
            MotorPhonemePrograms._expected_target = function

    # Adds a plan to the MPP, which is consumed at the next timeframe
    def addPlan(self, targets):
        self.__plan += targets
        self.__advance()  # raises UnrecoverableException

    # Used for logging purposes
    def getCurrentTarget(self):
        return np.array(self.__command.target)

    # Moves the command along as trajectories
    # i.e. calculates the 0th derivative of the system
    def time(self, state):
        end = False
        # Condition for plan advancement
        if self.__error(state) < self.__max_error:
            # end "requests" a new plan
            end = self.__advance()  # raises UnrecoverableException
        return end, self.__command.y()

    # This function was meant to control the vocal tract through velocity
    # It is not currently in use as the system uses trajectory functions
    def vtime(self, state):
        end = False
        if self.__error(state) < self.__max_error:
            end = self.__advance()  # raises UnrecoverableException
        acc = self.__command.time()
        return end, acc


# Definitions for interface purposes:
def setTargetSanitizer(function):
    MotorPhonemePrograms.setSanitizingFunction(function)
