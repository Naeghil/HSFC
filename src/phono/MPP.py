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


# A command is in terms of distance and effort, where effort is the inverse of the period
class MotorPhonemePrograms:
    def __init__(self):
        self.__last_command = None  # Velocity
        pass

    # See equation v_A
    # v(t)= d(2(f^3)(t^2)-t(f+4f^2))e^(-ft)
    def __Birkolz(self, t):
        pass