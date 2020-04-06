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
import numpy as np

from src.utils.utils import plot
from src.vtract.paraminfo import VTParametersInfo as PI
import src.utils.paramlists as PL

f_rate = 2000
dur_s = .5
no_frames = int(round(f_rate * dur_s))


# This tests merely that the api is connected and produces audio,
# as well as basic functionalities of the vocal tract
# Success: silent audio is produced
def testDefault(orch):
    print('Testing default position')
    vt = orch.vt
    for t in range(no_frames):
        vt.time(t, None, False)
    vt.close(no_frames, 'defo')


# This tests that the VocalTract class can actually move the articulators,
# by specifying a velocity, relative to a cubic polynomial trajectory
# Success: target vowel is produced, plot consistent with trajectory
def testTargets(orch, target, t_label):
    vt = orch.vt
    print('Testing vowel target: ' + t_label)
    s0 = vt.getState()
    lb = PI.vlabels
    dy = np.array(target, dtype='f8') - s0
    # Parameters to test:
    t_max = 0.007  # s, time for articulation of vowel
    a_frames = int(round(f_rate * t_max))  # Frames for articulation of vowel
    v_frames = int(a_frames / 2)  # Frames for vocalization
    trajectory = [s0]

    # v(t)= 3(t-1)^2    [v(0)=3]
    def vel(time):
        return 1 + (time-1)**3

    for t in range(no_frames):
        v = None
        if t in range(a_frames):
            inst_vel = vel((t + 1) / a_frames) - vel(t / a_frames)
            v = dy * inst_vel
            v[-4] = (1000.0 / v_frames) if (t > a_frames - v_frames - 1) else 0.0
        l = -(t - no_frames + 20)
        if l in range(a_frames):
            inst_vel = vel(l / a_frames) - vel((l + 1) / a_frames)
            v = {key: dy[key] * inst_vel for key in dy.keys()}
            v[-4] = (-1000.0 / v_frames) if (l > a_frames - v_frames - 1) else 0.0

        vtin = PL.Velocity(v)
        vt.time(t, vtin, False)
        trajectory.append(vt.getState())

    plt = np.array(trajectory).T
    rem_idxs = [21, 22, 23, 27]
    plt = np.delete(plt, rem_idxs, axis=0)
    rest = np.delete(s0, rem_idxs)
    tar = np.delete(np.array(target, dtype='f8'), rem_idxs)
    # Initial/Final: black
    # Target: green
    plot.plot_all(plt, [rest, tar], ['k', 'g'], len(trajectory))

    vt.close(no_frames, t_label)
