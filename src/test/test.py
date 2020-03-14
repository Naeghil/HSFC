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
import sys
import math
import matplotlib.pyplot as pl
import src.utils.paramlists as PL
import numpy as np

f_rate = 1000
dur_s = .5
no_frames = int(round(f_rate * dur_s))


# Target movement candidates:
# v(t)= -2t+2       [v(0)=2]
def sqpolv(t):
    return -t ** 2 + 2 * t


# v(t)= (e-1)/t     [v(0)=inf]
def logv(t):
    return math.log((math.e - 1) * t + 1)


# v(t)= 1/(2*sqrt(t))[v(0)=inf]
def sqrtv(t):
    return math.sqrt(t)


# v(t)= 3(t-1)^2    [v(0)=3]
def cupolv(t):
    return 1 + (t - 1) ** 3


def testDefault(vt):
    print('Testing default position')
    for t in range(no_frames):
        vt.time(t, None, False)
    vt.close(no_frames, 'defo')


def testTargets(vt, target, t_label):
    print('Testing vowel target: ' + t_label)
    s0 = vt.getState().asFrame()[0]
    lb = PL.ParList.vlabels
    dy = {lb[i]: round(target[i] - s0[i], 6) for i in range(len(lb))}
    # Parameters to test:
    t_max = 0.007  # s, time for articulation of vowel
    a_frames = int(round(f_rate * t_max))  # Frames for articulation of vowel
    v_frames = int(a_frames / 2)

    vel = cupolv

    for t in range(no_frames):
        v = None
        if t in range(a_frames):
            inst_vel = vel((t + 1) / a_frames) - vel(t / a_frames)
            v = {key: dy[key] * inst_vel for key in dy.keys()}
            v['d_rest'] = .00005 if (t == a_frames - 1) else 0.0
            v['f0'] = 0.0
            v['pressure'] = (1000.0 / v_frames) if (t > a_frames - v_frames - 1) else 0.0
        l = -(t - no_frames + 20)
        if l in range(a_frames):
            inst_vel = vel(l / a_frames) - vel((l + 1) / a_frames)
            v = {key: dy[key] * inst_vel for key in dy.keys()}
            v['d_rest'] = -.00005 if (l == a_frames - 1) else 0.0
            v['f0'] = 0.0
            v['pressure'] = (-1000.0 / v_frames) if (l > a_frames - v_frames - 1) else 0.0

        vtin = PL.Velocity(v)
        vt.time(t, vtin, False)

    vt.close(no_frames, t_label)


def testSyllable(vt, vtarget, vlabel, ctarget, clabel):
    print('Testing syllable: ' + clabel + "/" + vlabel)
    state = vt.getState()
    lb = PL.ParList.vlabels+['pressure', 'd_rest', 'f0']
    s0 = state.asFrame()[0]+state.get('pressure')+state.get('upper_rest_displacement')+state.get('f0')

    T1 = .001  # Time constant for consonant approach
    ct = ctarget+[0.0, 0.00015, 120.0]
    T2 = 0.001  # Time constant for phonation
    pt = ctarget+[1000.0, 0.0015, 120.0]  # .05/0.15 /b/ /d/, 0.25mm g
    # 7ms for /l/, 15ms for /b/, /d/, /g/, and /r/, 25ms for /m/ and /n/
    T3 = 0.025  # Time constant for vowel approach
    vt = vtarget+[1000.0, 0.0015]  # always 0.15 for vowel
    T4 = 0.030  # Time constant for relaxation

    vel_raw = np.array([0.0]*len(s0), dtype='f4')

    # TODO: if mc works, this is an opportunity for "feedback" implementation since sensory channel knows timing and
    #  targets; simply think of time constant as about 1 - activation
    # TODO: still to do
    for t in range(frames):
        v = None
        # 1. Consonant Approach and Phonation
        if t in range(frames1):
            inst_vel = vel((t + 1) / frames1) - vel(t / frames1)
            v = {key: d1[key] * inst_vel for key in d1.keys()}
        # 3. Vowel approach
        tv = t - frames1
        if tv in range(frames2):
            inst_vel = vel((tv + 1) / frames1) - vel(tv / frames1)
            v = {key: d2[key] * inst_vel for key in d2.keys()}
        # 4. Rest position
        tr = t - (frames1 + frames2 + 300)
        if tr in range(frames3):
            inst_vel = vel((tr + 1) / frames1) - vel(tr / frames1)
            v = {key: d3[key] * inst_vel for key in d3.keys()}
        vtin = PL.Velocity(v)
        vt.time(t, vtin, False)
    vt.close(frames, "try")


def main():
    pass


if __name__ == '__main__':
    main()
