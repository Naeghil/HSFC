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

import sys
import math
import matplotlib.pyplot as pl
import src.utils.paramlists as PL

# Paths to the packages
import src.vtract

f_rate = 400
dur_s = .5
no_frames = int(round(f_rate * dur_s))


# The idea is: in "1 unit" to reach 100% of the difference between current state and target
# For the instantaneous velocity, we use the definite integral
# Target movement candidates:
# x(t)= -t^2+2t
# v(t)= -2t+2       [v(0)=2]
def sqpolv(t):
    return -t ** 2 + 2 * t


# x(t)= ln((e-1)t+1)
# v(t)= (e-1)/t     [v(0)=inf]
def logv(t):
    return math.log((math.e - 1) * t + 1)


# x(t)= sqrt(t)
# v(t)= 1/(2*sqrt(t))[v(0)=inf]
def sqrtv(t):
    return math.sqrt(t)


# x(t)= (x-1)^3 + 1
# v(t)= 3(t-1)^2    [v(0)=3]
def cupolv(t):
    return 1 + (t - 1) ** 3


def testDefault(vt):
    print('Testing default position')
    for t in range(no_frames):
        vt.time(t, None, False)
    vt.close(no_frames, 'defo')


# Available targets:
# 'a', 'e', 'i', 'o', 'u', 'E:', '2', 'y', 'A', 'I', 'E', 'O', 'U', '9', 'Y', '@', '@6'
# Tests routine of:
# 1. a_frames-1 frame of movement start
# 2. v_frames to reach full vocalisation (pressure=1000.0)
# 3. n frames of sound (no operations)
# 4. v_frames to stop vocalisation
# 5. a_frames*2-1 frames to return to initial position
def testTargets(vt, target, t_label):
    print('Testing vowel target: ' + t_label)
    s0 = vt.getState()
    lb = PL.ParList.vlabels
    dy = {lb[i]: (target[i] - s0.get(lb[i])) for i in range(len(lb))}

    # Parameters to test:
    t_max = 0.007  # s, time for articulation of vowel
    a_frames = int(round(f_rate * t_max))  # Frames for articulation of vowel
    v_frames = int(a_frames / 2)


    # The velocity function to use
    vel = cupolv

    for t in range(no_frames):
        v = None
        if 0 <= t < a_frames - 1:
            inst_vel = vel((t + 1) / a_frames) - vel(t / a_frames)
            v = {key: dy[key] * inst_vel for key in dy.keys()}
            v['d_rest'] = 0.0
            v['f0'] = 0.0
            v['pressure'] = (1000.0 / v_frames) if (t > a_frames - v_frames - 2) else 0.0
        l = no_frames - t - 20
        if 0 <= l < a_frames - 1:
            inst_vel = vel(l / a_frames) - vel((l + 1) / a_frames)
            v = {key: dy[key] * inst_vel for key in dy.keys()}
            v['d_rest'] = 0.0
            v['f0'] = 0.0
            v['pressure'] = (-1000.0 / v_frames) if l > a_frames - v_frames - 2 else  0.0

        vtin = PL.Velocity(v) if v else None
        vt.time(t, vtin, False)

    vt.close(no_frames, t_label)


if __name__ == '__main__':
    y0 = 0.0
    yt = 1.0
    T = 1000.0
    t = 0
    v = 0.0
    y = [y0]
    e = 1.0 * ((yt - y0))

    while abs(y[t] - yt) > 0.03:
        d = (yt - y[t])
        v += d * 4 / (T ** 2) * pow(math.e, -t * d / T)
        # v = (y[t]-(y[t]**2)/yt)*(1.0/T)
        # v = (yt-y[t])*(1.0/T)
        # Motor, doesn't know shit
        # v = (e/T)*pow(math.e, -t/T)
        y.append(y[t] + v)
        t += 1

    pl.plot(y)
    pl.show()
