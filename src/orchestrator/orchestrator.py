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
import numpy as np
from matplotlib import pyplot as pl

from . import init_utils as init
import src.vtract.expose as vtract
import src.phono.expose as phono
from src.syll.MSP import MotorSyllablePrograms
from ..utils.paramlists import Target


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
            self.vt = vtract.VocalTract(synth, conf['qred'], self.param_info.getDefaults())
            print('  Initializing motor controller...')
            s0 = self.vt.getState()
            self.mpp = phono.MotorPhonemePrograms(s0, conf['frate'])

        except Exception as e:
            print('Initialization failed: ', e)
            if self.vt:
                self.vt.close()
            sys.exit()

        self.log = []  # Logs past utterances as (input_string, states_list, targets_list, audio)
        self.current_utterance = ""
        self.current_log = []
        self.targets_log = []

    def __plot(self):
        plt = np.array(self.current_log).T
        tars = np.array(self.targets_log).T
        labels = np.array(vtract.VTParametersInfo.working_labels)
        rem_idxs = [21, 22, 23, 27]
        plt = np.delete(plt, rem_idxs, axis=0)
        tars = np.delete(tars, rem_idxs, axis=0)
        labels = np.delete(labels, rem_idxs, axis=0)

        fig = pl.figure()
        par_no = plt.shape[0]
        for i in range(par_no):
            sf = fig.add_subplot(6, 4, i + 1)
            sf.set_title(labels[i])
            sf.plot(plt[i], 'b')
            sf.plot(tars[i], 'g')

        pl.subplots_adjust(left=0.05, right=0.99, top=0.95, bottom=0.05, hspace=1.0)

        pl.show()

    # Once ha motor plan has been executed, the utterance is synthesized and its data is logged and flushed
    # At the end, the system is ready for a new word
    def speak(self):
        audio = self.vt.speak(self.current_utterance)
        self.log.append((self.current_utterance, self.current_log, audio))
        self.current_log = []
        self.targets_log = []

    def time(self):
        end, new = self.mpp.ttime(self.vt.getState())
        self.current_log.append(new)
        self.targets_log.append(self.mpp.getCurrentTarget())
        self.vt.setState(Target(1.0, new))
        if end:
            if 1 == 1:  # Turn on/off the graphing function
                self.__plot()
            self.speak()
        return end

    # This function needs to be used because of the c_types in the api
    def terminate(self):
        if self.vt:
            self.vt.close()
