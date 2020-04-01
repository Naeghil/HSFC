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

import matplotlib.pyplot as pl
from src.utils.paramlists import Target
import numpy as np
import src.phono.MPP as mpp


# This tests the MPP and its functions as a "command-maker"
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

    # TODO: if mc works, use it for "feedback" implementation since sensory channel knows timing and targets
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
#    '''
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


class plot:
    @staticmethod
    def plot_all(data, tars, tar_cols, x_max):
        # Initial/Final: black
        # Consonant: green
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


if __name__ == '__main__':
    pass
