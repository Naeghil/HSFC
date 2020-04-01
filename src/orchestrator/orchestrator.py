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
import src.phono.expose as phono
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
            print('Initializing submodules...')
            print('  Loading somatophoneme targets...')
            self.spt = phono.SomatoPhonemeTargets(0.0)
            print('  Initializing motor planner...')
            self.msp = MotorSyllablePrograms(self.spt.targets)
            print('  Initializing vocal tract...')
            # audiopath = conf['path'] + os.sep + 'Output' + os.sep
            self.vt = vtract.VocalTract(synth, conf['fsynth'], self.param_info.getDefaults())
            print('  Initializing motor controller...')
            s0 = self.vt.getState()
            self.mpp = phono.MotorPhonemePrograms(s0, conf['frate'])

        except Exception as e:
            print('Initialization failed: ', e)
            if self.vt:
                self.vt.close()
            sys.exit()

        self.log = []  # Logs past utterances as (input_string, states_list, audio)
        self.current_utterance = ""
        self.current_log = []

    # Once ha motor plan has been executed, the utterance is synthesized and its data is logged and flushed
    # At the end, the system is ready for a new word
    def speak(self):
        audio = self.vt.speak(self.current_utterance)
        self.log.append((self.current_utterance, self.current_log, audio))
        self.current_log = []

    # This function needs to be used because of the c_types in the api
    def terminate(self):
        if self.vt:
            self.vt.close()
