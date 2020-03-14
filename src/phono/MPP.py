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
import numpy as np
import src.phono.motcommand as mc


# A command is in terms of distance and effort, where effort is the inverse of the period
class BirkholzMotorControl:
    def __init__(self, initial, command_list):  # The latter is a list of tuples (target, time_costant)
        self.__plan = command_list
        first = self.__plan.pop(0)
        self.__command = mc.MotorCommand(first[0], first[1], initial)

    def addStep(self, target, time_constant):
        self.__plan.append((target, time_constant))

    def time(self):
        acc, end = self.__command.time()
        if end and len(self.__plan) is not 0:
            new = self.__plan.pop(0)
            self.__command = mc.MotorCommand(new[0], new[1], self.__command.getFinalValues())
        # If there is no more commands it means the VT should keep approaching the target
        return acc

    def stopMotorActivation(self):
        self.__plan = []
        tar = self.__command.getFinalValues()
        self.__command = mc.MotorCommand(tar, 1.0, tar)


# Change this to change the approach:
MotorPhonemePrograms = BirkholzMotorControl
