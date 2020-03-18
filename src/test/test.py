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
import copy
import math
from scipy.special import binom as ch

import matplotlib.pyplot as pl
import src.utils.paramlists as PL
import numpy as np
import src.phono.MPP as mpp

f_rate = 2000

N = 6  # Order of the system


# Single command version
def make_command(inits, T: float, tar: float):
    c_list = make_constants(inits, T, tar)
    def y(t, n=0):
        res = 0.0
        a = -1.0/T
        for i in range(len(c_list)):
            qi = 0.0
            for k in range(min(N-i, n+1)):
                qi += a**(n-k)*float(ch(n,k))*c_list[i+k]*float(math.factorial(k+i))/float(math.factorial(i))
            res += qi*(t**i)
        res *= math.e**(t*a)
        res += (tar if n is 0 else 0.0)
        return res
    return y


def make_constants(inits, T, tar):
    a = -1.0/T
    c = [inits[0]-tar]
    for i in range(1, N):
        d = 0.0
        for k in range(i):
            d += c[k]*(a**(i-k))*float(math.factorial(i))/float(math.factorial(i-k))
        ci = (inits[i] - d)/float(math.factorial(i))
        c.append(ci)
    return c

def testSyllable(VT, vtarget, vlabel, ctarget, clabel):
    print('Testing syllable: ' + clabel + "/" + vlabel)
    state = VT.getState()
    lb = PL.ParList.vlabels + ['pressure', 'd_rest', 'f0']
    par_no = len(lb)
    s0 = state.asFrame()[0] + [state.get('pressure'), state.get('upper_rest_displacement'), state.get('f0')]
    T1 = 0.01 * f_rate  # Time constant for consonant approach
    ct = ctarget + [0.0, 0.00015, 120.0]
    T2 = 0.001 * f_rate  # Time constant for phonation
    pt = ctarget + [1000.0, 0.0015, 120.0]  # .05/0.15 /b/ /d/, 0.25mm g
    # 7ms for /l/, 15ms for /b/, /d/, /g/, and /r/, 25ms for /m/ and /n/
    T3 = 0.025 * f_rate  # Time constant for vowel approach
    vt = vtarget + [1000.0, 0.0015, 120.0]  # always 0.15 for vowel
    T4 = 0.030 * f_rate  # Time constant for relaxation

    vel_raw = np.array([0.0] * len(s0), dtype='f8')
    y = np.array(s0, dtype='f8')
    ft = np.array(s0, dtype='f8')

    # plan = [(ct, T1)]
    # plan = [(ct, T1), (pt, T2), (vt, T3), (s0, T4)]
    plan = [(ct, T1), (vt, T3), (s0, T4)]
    current_target = 0

    initial = np.array(s0+[0.0]*par_no*5).reshape((6, par_no))
    MPP = mpp.MotorPhonemePrograms(initial, plan)
    # TODO: if mc works, this is an opportunity for "feedback" implementation since sensory channel knows timing and
    #  targets; simply think of time constant as about 1 - activation
    t = 0
    frames = [copy.deepcopy(y)]
    while True:
        vel_raw += MPP.time()
        y += vel_raw
        frames.append(copy.deepcopy(y))
        t += 1
#        if ((y-ct)**2).mean() < 0.1: break
        if t >= 5000: break

    print(s0[0])
    print(ct[0])
    print(vt[0])

    plt = np.array(frames).T
    # Initial/Final: black
    # Consonant: green
    # Phonation blue
    # Vowel: red
#    plot.plot_all(plt, [s0, pt, ct, vt], ['k', 'b', 'g', 'r'], t+1, lb)
    i = 0
    plot.plot(plt[i], [s0[i], pt[i], ct[i], vt[i]], ['k', 'b', 'g', 'r'], t+1)

    # VT.close(t, "try")
    VT.close()


class plot:
    def plot_all(data, tars, tar_cols, x_max, lb):
        # Initial/Final: black
        # Consonant: green
        # Phonation blue
        # Vowel: red
        fig = pl.figure()
        par_no = data.shape[0]
        for i in range(par_no):
            if i in range(21, 24): continue
            p = i + 1 if i < 21 else i - 2
            sf = fig.add_subplot(6, 4, p)
            sf.plot(data[i])
            for idx in range(len(tars)):
                sf.plot([tars[idx][i]]*x_max, tar_cols[idx])

            sf.set_title(lb[i])
        pl.subplots_adjust(hspace=1.0)
        pl.show()

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
    inits = [0.0]*6
    inits[0] = 1.0
    tar1 = 0.0
    T1 = 10.0
    tar2 = 0.3296
    T2 = 25.0

    plan = [(tar2, T2)]
    current = tar1
    y = make_command(inits, T1, tar1)
    x = []
    t = 0.0
    off_t = 0.0
    while t <= 400.0:
        x.append(y(t-off_t))
        t += 0.2
        # TODO: check what the error does
        if (x[-1]-current)**2 < 1.0 and len(plan) is not 0:
            current, tt = plan.pop(0)
            new_inits = []
            for i in range(N):
                new_inits.append(y(t-off_t,i))
            y = make_command(new_inits, tt, current)
            off_t = t
            print('Changed at '+str(t))

    plot.plot(x, [inits[0], tar1, tar2], ['k', 'g','r'], len(x))

if __name__ == '__main__':
    try:
        main()
    except Exception as err:
        print(err)