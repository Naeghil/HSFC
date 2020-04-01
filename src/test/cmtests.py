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

from src.utils.utils import plot


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


# TODO: rework this function
'''# This tests the MPP and its functions as a "command-maker"
# Success: the syllable is produced and the graphs are consistent, showing no overshooting
def testSyllable(VT, rest, vtarget, vlabel, ctarget, clabel):
    print('Testing syllable: ' + clabel + "/" + vlabel)
    # Setting up plan; this is the responsibility of the higher level module MSP
    err: float = 0.04
    par_no = len(rest)
    inits = np.array(rest + [0.0] * par_no * 5, dtype='f8').reshape(6, par_no)  # Initial dynamical state
    tar1 = Target(4.0, ctarget)  # Phoned consonant
    tarpp = tar1.makeNonPhonatory(10.0)  # Consonant approach
    # 7ms for /l/, 15ms for /b/, /d/, /g/, and /r/, 25ms for /m/ and /n/
    tar2 = Target(25.0, vtarget)  # always 0.15 for vowel
    tarnp = tar2.makeNonPhonatory(4.0)
    trest = Target(10.0, rest)
    plan = [tarpp, tar1, tar2, tarnp, trest]
    # Initialize MPP
    MPP = mpp.MotorPhonemePrograms(inits, plan, 1000)

    # vel_raw = np.array([0.0] * len(s0), dtype='f8')

    np.set_printoptions(4, suppress=True)

    frames = [np.array(rest, dtype='f8')]
    t = 0
    while True:
        curr = MPP.ttime()
        frames.append(curr)
        VT.setState(Target(1.0, curr))
        t += 1
        if (np.square(curr - MPP.current_target())).mean() < err:
            if not MPP.advance():
                break
            # if t > 100: break

    plt = np.array(frames).T
    rem_idxs = [21, 22, 23, 27]
    plt = np.delete(plt, rem_idxs, axis=0)
    s0 = np.delete(rest, rem_idxs)
    tar1 = np.delete(tar1.asTargetParameters(), rem_idxs)
    tar2 = np.delete(tar2.asTargetParameters(), rem_idxs)
    # Initial/Final: black
    # Consonant: blue
    # Phonation green
    # Vowel: red
    plot.plot_all(plt, [s0, tar1, tar2], ['k', 'g', 'r'], len(frames))
    # Synthesizes or not the audio
    if 1 == 1:
        VT.close(t, "try")
    else:
        VT.close()
'''