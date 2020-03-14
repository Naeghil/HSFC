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
import scipy as sp
import numpy as np
from math import e as e
from math import factorial as fact


# Sixth order differential equation
class MotorCommand:
    n = 6  # The order of the command

    def __init__(self, target,  # The initial target of the command
                 t_max,         # Time constraint (in frames)
                 fn_t0=None):   # List of initial values (list of parameters) for the function and its derivatives
        # Preparatory checks and conversions
        if fn_t0 is None or len(fn_t0) is not self.n:
            raise TypeError("Wrong number of initial parameters")
        parno = len(target)
        initial_values = np.array(fn_t0).reshape(self.n, parno)

        self.c = np.empty((self.n, parno), dtype='f4')  # Constants for the equation
        self.__vel_constants = np.empty((self.n, parno), dtype='f4')  # These are actually used for the velocity
        self.t = 0.0              # Internal time
        self.T = float(t_max)     # Time for which the command is active
        self.target = np.array(target) # Target to reach

        a = -1.0/self.T
        # This assumes target is of the same length as the initial values, which should be so
        # Calculate all the constants TODO: reference this procedure
        self.c[0] = initial_values[0] - self.target     # c_0
        for n in range(1, self.n):
            d = np.empty(parno, dtype='f4')
            for i in range(n):
                d += self.c[i]*(a**(n-i))*ch(n, i)*fact(i)
            cn = (initial_values[n] - d)/fact(n)
            self.c[n] = cn

        # Calculate all the constants for velocity TODO: reference this procedure
        for n in range(self.n-1):
            self.__vel_constants[n] = a*self.c[n]+(n+1)*self.c[n+1]
        self.__vel_constants[5] = a*self.c[5]

    def __calc_function(self, t):
        y = np.array([0.0]*self.c.shape[1], dtype='f4')
        for i in range(self.n):
            y += self.c[i]*(t**i)
        y = y*(e**(-t/self.T))+self.target
        return y

    def __calc_vel(self, t):
        y = np.array([0.0] * self.c.shape[1], dtype='f4')
        for i in range(self.n):
            y += self.__vel_constants[i] * (t ** i)
        y = y * (e ** (-t / self.T))
        return y

    def __calc_derivative(self, n, t):
        a = -1.0/self.T
        res = np.array([0.0] * self.c.shape[1], dtype='f4')
        for i in range(self.n):
            qi = np.array([0.0] * self.c.shape[1], dtype='f4')
            for k in range(min(self.n-i, n+1)):
                qi += (a**n-k)*ch(n,k)*self.c[i+k]*fact(k+i)/fact(i)
            res += (t**i)*qi
        return res*(e**(a*t))

    def time(self):
        acc = self.__calc_vel(self.t+1.0) - self.__calc_vel(self.t)
        self.t += 1.0
        return acc, self.t >= self.T

    def getConstants(self):
        return copy.deepcopy(self.c)

    def getFinalValues(self):
        fin = np.empty(self.n)
        for i in range(self.n):
            fin[i] = self.__calc_derivative(i, self.T)
        return fin
