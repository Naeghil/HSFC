# -------------------------------------------------------------------------------
# Name:        Orchestrator
# Purpose:     Module handling the system components, on a separate thread
#
# Author:      Roberto Sautto
#
# Created:     04/03/2020
# Copyright:   (c) Roberto Sautto 2020
# Licence:     <your licence>
# -------------------------------------------------------------------------------
# TODO: do the threading thing
import sys

# Local imports:
from . import init_utils as init
import src.vtract.expose as vtract
import src.utils.paramlists as PL
from src.phono.SPT import SomatoPhonemeTargets
from src.syll.MSP import MotorSyllablePrograms


class Orchestrator:
    def __init__(self, path, details):  # Essentially initializes all system submodules
        try:
            conf, synth, self.param_info = init.preliminaryInitialization(path, details)
        except Exception as e:
            print('Loading configuration failed: ', e)
            sys.exit()

        # Components initialization:
        try:
            print('Loading somatophoneme targets...')
            self.spt = SomatoPhonemeTargets(0.0)
            print('Initializing motor planner...')
            self.msp = MotorSyllablePrograms(self.spt.targets)
            print('Initializing vocal tract...')
            # audiopath = conf['path'] + os.sep + 'Output' + os.sep
            self.vt = vtract.VocalTract(synth, conf['fsynth'], self.param_info.getDefaults())

        except Exception as e:
            print('Initialization failed: ', e)
            if self.vt:
                self.vt.close()
            sys.exit()

    def terminate(self):
        if self.vt:
            self.vt.close()
