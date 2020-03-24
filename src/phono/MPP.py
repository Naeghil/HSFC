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
import src.phono.motcommand as mc


# A command is in terms of distance and effort, where effort is the inverse of the period
class BirkholzMotorControl:
    # TODO: command_list will be a "Plan"
    def __init__(self, initial, command_list, frate=None):
        self.__plan = command_list
        self.__progression = 0  # Index of the current command
        if frate is None:
            self.__dt = 1.0
        else:
            self.__dt = 1000.0/frate  # dt is in ms
        self.__command = mc.MotorCommand(self.__plan[0], initial, self.__dt)

    def addStep(self, target):
        self.__plan.append(target)

    # TODO: for testing purposes
    def ttime(self):
        return self.__command.y()

    # TODO: for testing purposes
    def current_target(self):
        return self.__command.target

    def time(self):
        acc = self.__command.time()
        # if end and len(self.__plan) is not 0:
        # TODO: advancement conditions
        # If there is no more commands it means the VT should keep approaching the target
        return acc

    # TODO: consider making this private:
    def advance(self):
        if self.__progression < len(self.__plan) - 1:
            self.__progression += 1
            self.__command = mc.MotorCommand(self.__plan[self.__progression],
                                             self.__command.getFinalValues(), self.__dt)
            return True
        return False

    def stopMotorActivation(self):
        self.__plan = []
        tar = self.__command.getFinalValues()
        self.__command = mc.MotorCommand(tar, 1.0, tar)


# Change this to change the approach:
MotorPhonemePrograms = BirkholzMotorControl
