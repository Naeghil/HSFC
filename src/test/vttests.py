# -------------------------------------------------------------------------------
# Name:        Tests made for the vocal tract production of sound
# Purpose:
#
# Author:      Roberto Sautto
#
# Created:     17/03/2020
# Copyright:   (c) Roberto Sautto 2020
# Licence:     <your licence>
# -------------------------------------------------------------------------------
import math
import src.utils.paramlists as PL

f_rate = 2000
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
