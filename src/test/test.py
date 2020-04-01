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
from src.orchestrator.orchestrator import Orchestrator
from src.utils.paramlists import Target
from src.utils.utils import plot
import numpy as np


# This tests the MSP integrated in the system
def testMSP(orch: Orchestrator, in_str):
    print('Testing production: ' + in_str)
    orch.current_utterance = in_str
    plan = orch.msp.makePlan(in_str)
    orch.mpp.addPlan(plan)

    np.set_printoptions(4, suppress=True)
    frames = []
    t = 0
    while True:
        end, new = orch.mpp.ttime(orch.vt.getState())
        frames.append(new)
        orch.vt.setState(Target(1.0, new))
        t += 1
        if end:
            orch.speak()
            break

    plt = np.array(frames).T
    rem_idxs = [21, 22, 23, 27]
    plt = np.delete(plt, rem_idxs, axis=0)
    plot.plot_all(plt, [], [], len(frames))
    orch.terminate()
