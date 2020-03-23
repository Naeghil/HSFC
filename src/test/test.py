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

import matplotlib.pyplot as pl
from src.vtract.paraminfo import VTParametersInfo as PI
import numpy as np
import src.phono.MPP as mpp

f_rate = 1000

N = 6  # Order of the system


# Single command version
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


def testSyllable(VT, vtarget, vlabel, ctarget, clabel):
    # TODO: set up a second channel for phonation or change pressure target
    print('Testing syllable: ' + clabel + "/" + vlabel)
    # Settin up parameters
    lb = PI.vlabels + \
         ['pressure', 'lower_rest_displacement', 'upper_rest_displacement', 'f0']
    par_no = len(lb)
    # Set up of initial dynamic state:
    state = VT.getState()
    s0 = state.asFrame()[0] + \
         [state.get('pressure'), state.get('lower_rest_displacement'),
          state.get('upper_rest_displacement'), state.get('f0')]
    inits = np.array(s0 + [0.0] * par_no * 5, dtype='f8').reshape(6, par_no)
    # y = np.array(s0, dtype='f8')
    # Set up targets and plan
    err: float = 0.04
    tar1 = ctarget + [0.0, 0.00015, 0.00015, 120.0]
    T1 = 10.0  # Time constant for consonant approach
    tarp = ctarget + [1000.0, 0.00015, 0.00015, 120.0]  # .05/0.15 /b/ /d/, 0.25mm g; phonation target
    TP = 4.0  # Time constant for phonation
    tar2 = vtarget + [1000.0, 0.00015, 0.00015, 120.0]  # always 0.15 for vowel
    # 7ms for /l/, 15ms for /b/, /d/, /g/, and /r/, 25ms for /m/ and /n/
    T2 = 25.0  # Time constant for vowel approach
    T3 = 10.0  # Time constant for relaxation
    tarnp = vtarget + [0.0, 0.00015, 0.00015, 120.0]
    TNP = 4.0
    # plan = [(tar1, T1)]
    # plan = [(tar1, T1), (tarp, TP), (tar2, T2), (tarnp, TNP), (s0, T3)]
    plan = [(tar1, T1), (tarp, TP), (tar2, T2), (tarp, T1), (tar2, T2), (tarnp, TNP), (s0, T3)]
    # Initialize MPP
    MPP = mpp.MotorPhonemePrograms(inits, plan, f_rate)

    # vel_raw = np.array([0.0] * len(s0), dtype='f8')

    np.set_printoptions(4, suppress=True)

    # TODO: if mc works, use it for "feedback" implementation since sensory channel knows timing and targets
    frames = [np.array(s0, dtype='f8')]
    t = 0
    while True:
        curr = MPP.ttime()
        frames.append(curr)
        VT.setState(PL.ParList(curr))
        t += 1
        if (np.square(curr - MPP.current_target())).mean() < err:
            if not MPP.advance():
                break
            # if t > 100: break
#    '''
    plt = np.array(frames).T
    rem_idxs = [21, 22, 23, 27]
    plt = np.delete(plt, rem_idxs, axis=0)
    s0 = np.delete(s0, rem_idxs)
    tar1 = np.delete(tar1, rem_idxs)
    tarp = np.delete(tarp, rem_idxs)
    tar2 = np.delete(tar2, rem_idxs)
    # Initial/Final: black
    # Consonant: blue
    # Phonation green
    # Vowel: red
    plot.plot_all(plt, [s0, tar1, tarp, tar2], ['k', 'b', 'g', 'r'], len(frames))
    # i = 2
    # plot.plot(plt[i], [s0[i], tar1[i], tarp[i], tar2[i]], ['k', 'b', 'g', 'r'], plt[i].shape[0])
#    '''
    if 1 is 1:
        VT.close(t, "try")
    else:
        VT.close()


class plot:
    @staticmethod
    def plot_all(data, tars, tar_cols, x_max):
        # Initial/Final: black
        # Consonant: green
        # Phonation blue
        # Vowel: red
        fig = pl.figure()
        par_no = data.shape[0]
        for i in range(par_no):
            sf = fig.add_subplot(6, 4, i+1)
            sf.plot(data[i])
            for idx in range(len(tars)):
                sf.plot([tars[idx][i]] * x_max, tar_cols[idx])
        pl.subplots_adjust(hspace=1.0)
        pl.show()

    @staticmethod
    def plot(data, tars, tar_cols, x_max):
        # Initial/Final: black
        # Consonant: green
        # Phonation blue
        # Vowel: red
        pl.plot(data)
        for idx in range(len(tars)):
            pl.plot([tars[idx]] * x_max, tar_cols[idx])
        pl.show()


def main():
    inits = [0.0] * 6
    # inits[0] = 1.0
    tar0 = 1.0
    T0 = 4.0
    tar1 = 0.0
    T1 = 10.0
    tar2 = 0.3296
    T2 = 25.0

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


if __name__ == '__main__':
    try:
        main()
    except Exception as err:
        print(err)
