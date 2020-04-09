# -------------------------------------------------------------------------------
# Name:        motorcommand
# Purpose:     Reproduces the dynamic state of the vocal tract while attempting
#              to reach an asymptotic target, as specified in Birkholz 2010:
#              "Model-Based Reproduction of Articulatory Trajectories for Consonant–Vowel Sequences"
#              It is essentially reproducing a differential system.
#
# Author:      Roberto Sautto
#
# Last mod:    7/04/2020
# Copyright:   (c) Roberto Sautto 2020
# Licence:     <your licence>
# -------------------------------------------------------------------------------

# Global imports
from scipy.special import binom as ch
import numpy as np
from math import e as e
from math import factorial as fact
# Local imports
from ..utils.utils import UnrecoverableException


class MotorCommand:
    N = 6  # The order of the differential system representing the command,
    # as recommended in a separate paper (see Report)

    def __init__(self, target,  # The target of the command
                 fn_t0,         # List of initial values (list of parameters) for the function and its derivatives
                 dt):           # Time increment

        # Command variables:
        self.target = target.asTargetParameters()  # Target to reach
        self.a = target.getEffort()  # Effort
        self.p_no = self.target.shape[0]  # Number of parameters in the target
        self.c = np.empty((self.N, self.p_no), dtype='f8')  # Constants for the equation
        self.t = 0.0  # Internal time, used in the equation
        self.dt = dt  # Time increment, dependent on the framerate of the system

        # Validation; any failure does not depend on user input here
        if fn_t0 is None or fn_t0.shape != (self.N, self.p_no):
            raise UnrecoverableException(
                "Wrong number of initial parameters when building the commands. This is a bug.")

        # Calculate all the constants, as specified in the paper
        self.c[0] = fn_t0[0] - self.target
        for i in range(1, self.N):
            d = np.array([0.0]*self.p_no, dtype='f8')
            for k in range(i):
                d += self.c[k] * (self.a**(i-k)) * fact(i) / fact(i-k)
            cn = (fn_t0[i] - d) / fact(i)
            self.c[i] = cn

    # Calculates the derivative of order der up to self.N
    # This equation is specified in the paper
    def __y(self, t, der=0):
        y = np.array([0.0]*self.p_no, dtype='f8')
        for i in range(self.N):
            qi = np.array([0.0]*self.p_no, dtype='f8')
            for k in range(min(self.N-i, der + 1)):
                qi += (self.a**(der-k)) * (ch(der, k)) * self.c[i+k] * (fact(k+i)) / (fact(i))
            y += qi*(t**i)
        y = y*(e**(self.a*t))
        if der is 0: y += self.target
        return y

    # shorthand for the 0th derivative, which is the target function
    def y(self):
        self.t += self.dt
        return self.__y(self.t)

    # This function was meant to calculate the instantaneous acceleration of the system
    # Not currently in use, as the system is using direct trajectories
    def time(self):
        acc = self.__y(self.t+self.dt, 1) - self.__y(self.t, 1)
        self.t += self.dt
        return acc

    # Provides the "final values"; to be used during command switch
    # in order to provide the initial dynamic state for the next command
    def getFinalValues(self):
        fin = np.empty((self.N, self.target.shape[0]))
        for i in range(self.N):
            fin[i] = self.__y(self.t, i)
        return fin

# Tests are not being implemented for this module as it's merely the implementation of mathematical functions
