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

import numpy as np

from src.vtract.paraminfo import VTParametersInfo as PI
import src.utils.paramlists as PL

f_rate = 2000
dur_s = .5



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





def testTargets(vt, target, t_label):
    print('Testing vowel target: ' + t_label)
    s0 = np.array(vt.getState().asFrame()[0]+[0.0, 0.0, 0.0, 0.0], dtype='f8')
    lb = PI.vlabels
    dy = np.array(target, dtype='f8') - s0
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
