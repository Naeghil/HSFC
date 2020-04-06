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
import numpy as np


# This tests the MSP integrated in the system
def testMSP(orch: Orchestrator, in_str):
    print('Testing production: ' + in_str)
    orch.current_utterance = in_str
    plan = orch.msp.makePlan(in_str)
    orch.mpp.addPlan(plan)
    orch.targets_log = list(t.asTargetParameters() for t in plan)

    np.set_printoptions(4, suppress=True)

    for t in range(4000):
        if orch.time():
            if t == 3999:
                orch.speak()
            break
