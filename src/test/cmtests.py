# -------------------------------------------------------------------------------
# Name:        Test script
# Purpose:
#
# Author:      Roberto Sautto
#
# Created:     15/02/2020
# Copyright:   (c) Roberto Sautto 2020
# Licence:     <your licence>
# -------------------------------------------------------------------------------
import math
from scipy.special import binom as ch

from .test import plot


# This tests the Birkholz Equations in a "convenient" single-parameter version
# The aim of this function is to "experiment" with various values of constants and targets
# Success: the targets are reached and the graph shows no overshooting or unacceptable undershooting
def testBirkholzEquations(init=0.0, tar0=1.0, T0=4.0, tar1=0.0, T1=10.0, tar2=0.3296, T2=25.0):
    N = 6  # Order of the system

    # Single command version of the birkholz equations
    def make_command(inits, T: float, tar: float):
        c_list = make_constants(inits, T, tar)

        def y(t, n=0):
            res = 0.0
            a = -1.0 / T
            for i in range(len(c_list)):
                qi = 0.0
                for k in range(min(N - i, n + 1)):
                    qi += a ** (n - k) * float(ch(n, k)) * c_list[i + k] * float(math.factorial(k + i)) / float(
                        math.factorial(i))
                res += qi * (t ** i)
            res *= math.e ** (t * a)
            res += (tar if n is 0 else 0.0)
            return res
        return y

    def make_constants(inits, T, tar):
        a = -1.0 / T
        c = [inits[0] - tar]
        for i in range(1, N):
            d = 0.0
            for k in range(i):
                d += c[k] * (a ** (i - k)) * float(math.factorial(i)) / float(math.factorial(i - k))
            ci = (inits[i] - d) / float(math.factorial(i))
            c.append(ci)
        return c

    inits = [init] + [0.0] * 5
    plan = [(tar1, T1), (tar2, T2)]
    current = tar0
    y = make_command(inits, T0, tar0)
    x = []
    t = 0.0
    off_t = 0.0
    while t <= 400.0:
        x.append(y(t - off_t))
        t += 0.2
        if (x[-1] - current) ** 2 < 0.05 and len(plan) is not 0:
            current, tt = plan.pop(0)
            new_inits = []
            for i in range(N):
                new_inits.append(y(t - off_t, i))
            y = make_command(new_inits, tt, current)
            off_t = t
            print('Changed at ' + str(t))

    plot.plot(x, [inits[0], tar0, tar1, tar2], ['m', 'k', 'g', 'r'], len(x))
