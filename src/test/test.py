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

# Paths to the packages
import src.vtract

f_rate = 1000
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
    s0 = vt.getState().asFrame()[0]
    lb = PL.ParList.vlabels
    dy = {lb[i]: round(target[i] - s0[i], 6) for i in range(len(lb))}
    # Parameters to test:
    t_max = 0.007  # s, time for articulation of vowel
    a_frames = int(round(f_rate * t_max))  # Frames for articulation of vowel
    v_frames = int(a_frames / 2)

    # The velocity function to use
    vel = cupolv

    for t in range(no_frames):
        v = None
        if t in range(0, a_frames):
            inst_vel = vel((t + 1) / a_frames) - vel(t / a_frames)
            v = {key: dy[key] * inst_vel for key in dy.keys()}
            v['d_rest'] = .00005 if (t == a_frames - 1) else 0.0
            v['f0'] = 0.0
            v['pressure'] = (1000.0 / v_frames) if (t > a_frames - v_frames - 1) else 0.0
        l = -(t - no_frames + 20)
        if l in range(0, a_frames):
            inst_vel = vel(l / a_frames) - vel((l + 1) / a_frames)
            v = {key: dy[key] * inst_vel for key in dy.keys()}
            v['d_rest'] = -.00005 if (l == a_frames - 1) else 0.0
            v['f0'] = 0.0
            v['pressure'] = (-1000.0 / v_frames) if (l > a_frames - v_frames - 1) else 0.0

        vtin = PL.Velocity(v)
        vt.time(t, vtin, False)

    vt.close(no_frames, t_label)


'''
Efference signals and the resulting forward predictions are part of the motor planning process from the start; 
(1) auditory phonological system defines the target of a speech act, which is activated by input from the lexical (lemma) level, 
    that also activates the associated motor phonological representation; 
(2) activated auditory target activates the associated motor representation, further reinforcing the motor activation, 
    while the activated motor representation sends an inhibitory signal to the auditory target; 
(3a) when there is a match between prediction and detection (that is, no corrections are necessary), 
     the signals will roughly cancel each other out; 
(3b) if , however, the wrong motor program is activated, it will then inhibit a non-target in the sensory system 
     and therefore leave the correction signal that is coming from the sensory target fully activated, 
     which in turn will continue to work towards activating the correct motor representation. 
Suppression of sensory target activity makes sense computationally for two reasons:
    One is to prevent interference with the next sensory target. In the context of connected speech, 
        auditory phonological targets (syllables) need to be activated in a rapid series. 
        Residual activation of a preceding phonological target may interfere with activation of a subsequent target if 
        the former is not quickly suppressed. An inhibitory motor-to-sensory input provides a mechanism for achieving this. 
    Target suppression can enhance detection of off-target sensory feedback
In the HSFC model, internal and external monitoring are just early and later phases, respectively, of the same mechanism. 
    In the early, internal phase, errors in motor planning fail to inhibit the driving activation of the sensory representation, 
    which acts as a 'correction' signal. 
    However, in the later, external monitoring phase, the sensory representation is suppressed.
'''


def berk_velocity(dist, f, ti):
    return dist * (2 * (f ** 3) * (ti ** 2) - ti * (5 * f ** 2)) * (math.e ** (-f * ti))


def v_change(d1, f1, d2, f2, t):
    return berk_velocity(d2, f2, 1+t) - berk_velocity(d1, f1, t)


def testPModule(begin, target, time):
    # Initialized tract:
    y_d = begin
    y_t = begin
    vel_d = 0.0
    vel_t = 0.0
    idist = target-begin
    dist = begin-target
    p_dist = begin-target
    trace_d = [y_d]
    trace_t = [y_t]

    for t in range(1 * int(time)):
        # SPT
        # 1. Activation from AST [0,1]
        # 2. Inhibition [-1, 0]
        #   a. Inhibition from sensory feedback (tight logistic) "we're here"
        #   b. Inhibition from prediction "where are we going"
        # MPP
        # 1. Activation from MSP
        # 2. Modulation from SPT
        effort1 = 1.0 / (time - t + 1) if (time - t + 1) != 0.0 else 0.0001
        effort2 = 1.0 / (time - t) if (time - t) != 0.0 else 0.0001
        vel_d += v_change(p_dist, effort1, dist, effort2, 0)
        vel_t += v_change(-idist, 1.0/time, -idist, 1.0/time, t)
        # VT
        y_d += vel_d
        y_t += vel_t
        p_dist = dist
        dist = y_d - target
        trace_d.append(copy.copy(y_d))
        trace_t.append(copy.copy(y_t))
    return [trace_d, trace_t]


def main():
    trace = testPModule(0.0, 1.0, 50.0)

    pl.plot(trace[0], 'b')
    pl.plot(trace[1], 'r')
    pl.show()


if __name__ == '__main__':
    main()
