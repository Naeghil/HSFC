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