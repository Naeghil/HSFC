# -------------------------------------------------------------------------------
# Name:        motorcommand
# Purpose:     inspired by the step-response idea in the Birkholz Papers TODO: actually pute citations
#
# Author:      Roberto Sautto
#
# Created:     15/02/2020
# Copyright:   (c) Roberto Sautto 2020
# Licence:     <your licence>
# -------------------------------------------------------------------------------
import copy

from scipy.special import binom as ch
import numpy as np
from math import e as e
from math import factorial as fact


# Sixth order differential equation
class MotorCommand:
    N = 6  # The order of the differential system representing the command

    def __init__(self, target,  # The target of the command
                 t_con,         # Time constant (in ms)
                 fn_t0,         # List of initial values (list of parameters) for the function and its derivatives
                 dt):           # Time increment
        # Preparatory checks and conversions
        if fn_t0 is None or \
                (fn_t0.shape[0] is not self.N and
                 fn_t0.shape[1] is not len(target)):
            raise TypeError("Wrong number of initial parameters")
        initial_values = np.array(fn_t0).reshape(self.N, len(target))
        # Instance variables:
        self.p_no = len(target)  # Number of parameters in the target
        self.c = np.empty((self.N, self.p_no), dtype='f8')  # Constants for the equation
        self.t = 0.0              # Internal time
        self.a = -1.0/t_con  # Effort
        self.dt = dt
        self.target = np.array(target)  # Target to reach


        # This assumes target is of the same length as the initial values, which should be so
        # Calculate all the constants TODO: reference this procedure
        self.c[0] = initial_values[0] - self.target     # c_0
        for i in range(1, self.N):
            d = np.array([0.0]*self.p_no, dtype='f8')
            for k in range(i):
                d += self.c[k] * (self.a**(i-k)) * fact(i) / fact(i-k)
            cn = (initial_values[i] - d) / fact(i)
            self.c[i] = cn

    # The equation is capable of calculating any derivative (der) up to self.N
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

    # TODO: for testing purposes
    def y(self):
        self.t += self.dt
        return self.__y(self.t)

    def time(self):
        acc = self.__y(self.t+self.dt, 1) - self.__y(self.t, 1)
        self.t += self.dt
        return acc

    def getConstants(self):
        return copy.deepcopy(self.c)

    def getFinalValues(self):
        fin = np.empty((self.N, self.target.shape[0]))
        for i in range(self.N):
            fin[i] = self.__y(self.t, i)
        return fin
