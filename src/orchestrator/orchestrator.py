# -------------------------------------------------------------------------------
# Name:        Orchestrator
# Purpose:     Handles the submodules of the system, running the main loop on a
#              separate thread, so as to leave the user interface always free for
#              more commands
#
# Author:      Roberto Sautto
#
# Last mod:    07/04/2020
# Copyright:   (c) Roberto Sautto 2020
# Licence:     <your licence>
# -------------------------------------------------------------------------------

# Global imports
from queue import Empty

import numpy as np
from matplotlib import pyplot as pl
from threading import Thread, Event
# Local imports:
from . import init_utils as init
import src.vtract.expose as vtract
import src.phono.expose as phono
from src.syll.MSP import MotorSyllablePrograms
from ..utils.paramlists import WorkingParList


class Orchestrator(Thread):
    def __init__(self, path, details, production_queue, bucket):  # Essentially initializes all system submodules
        super(Orchestrator, self).__init__()
        try:
            conf, synth, self.param_info = init.preliminaryInitialization(path, details)  # Raises FileNotFound
        except Exception as e:
            raise Exception('Loading configuration failed: \n'+str(e))

        # Components initialization:
        try:
            print('Initializing submodules...')
            print('  Loading somatophoneme targets...')
            self.__spt = phono.SomatoPhonemeTargets(conf['err'])
            print('  Initializing motor planner...')
            self.__msp = MotorSyllablePrograms(
                self.__spt.targets, self.__spt.vow_constants, self.__spt.con_constants)
            print('  Initializing vocal tract...')
            # audiopath = conf['path'] + os.sep + 'Output' + os.sep
            self.__vt = vtract.VocalTract(synth, conf['qred'], self.param_info.getDefaults())
            print('  Initializing motor controller...')
            s0 = self.__vt.getState()
            self.__mpp = phono.MotorPhonemePrograms(s0, conf['frate'], self.__spt.err)  # Raises ValueError
        except Exception as e:
            raise Exception('Initialization failed: \n'+str(e))
            if self.__vt:
                self.__vt.close()

        # Multithreading variables
        self.__kill = Event()  # Controls the loop in run()
        self.__toSay = production_queue  # Queue of utterances to speak
        # Bucket elements format: (requires_termination, message)
        self.__bucket = bucket  # Message passing back to calling thread
        # Logging variables
        self.__log = []  # Logs past utterances as (input_string, states_list, targets_list, audio)
        self.__current_utterance = None
        self.__current_log = []  # Temporary storage for logs
        self.__targets_log = []  # Temporary storage for logs
        # Other variables
        self.__displayPlot = details  # If true, each utterance will be plotted before being synthesized
        self.__max_time_letter = int(conf['frate']/2)  # Maximum frames allowed per character (0.5s)

    # Checking function for run()
    def __live(self):
        return not self.__kill.isSet()  # The "not" is a mere readibility sugar

    # Moves on to the next command if available, otherwise it waits
    def __commandSwitch(self):
        try:
            self.__current_utterance = self.__toSay.get(timeout=1)
            self.__toSay.task_done()
            plan = self.__msp.makePlan(self.__current_utterance)
            self.__mpp.addPlan(plan)  # raises ValueError
        except Empty:
            pass  # This is only needed in case the user terminates the program while in wait
        except ValueError as e:
            self.__bucket.put((True, "An error has been encountered while planning for " +
                               self.__current_utterance+':\n'+str(e)))

    # Merely a wrapper for the time function to avoid clogging the run() method
    def __safeTime(self, safe):
        # Gives 0.5 seconds per letter, which is more than enough
        if safe > len(self.__current_utterance) * self.__max_time_letter:
            self.__bucket.put((False,
                               "The current command for " + self.__current_utterance +
                               " has been reset because of timeout"))
            self.__reset()
            self.__vt.speak(self.__current_utterance)  # This flushes the synthesizer; it's unknown if it may get stuck
        else:
            self.time()

    # Resets logging variables
    def __reset(self):
        self.__current_log = []
        self.__targets_log = []
        self.__current_utterance = None

    # This function creates a plot of the vocal tract state, including its targets
    def __plot(self):
        toPlot = np.array(self.__current_log).T
        targets = np.array(self.__targets_log).T
        labels = np.array(vtract.VTParametersInfo.working_labels)
        # Some indexes are removed because they don't seem to contribute to production
        rem_idxs = [21, 22, 23, 27]
        toPlot = np.delete(toPlot, rem_idxs, axis=0)
        targets = np.delete(targets, rem_idxs, axis=0)
        labels = np.delete(labels, rem_idxs, axis=0)

        figure = pl.figure()
        par_no = toPlot.shape[0]
        for i in range(par_no):
            subplot = figure.add_subplot(6, 4, i + 1)
            subplot.set_title(labels[i])
            subplot.plot(toPlot[i], 'b')  # State in blue
            subplot.plot(targets[i], 'g')  # Targets in green

        pl.subplots_adjust(left=0.05, right=0.99, top=0.95, bottom=0.05, hspace=1.0)
        return pl

    # Once a motor plan has been executed, the utterance is synthesized and its data is logged and flushed
    # At the end, the system is ready for a new word
    def speak(self):
        audio = self.__vt.speak(self.__current_utterance)
        self.__log.append((self.__current_utterance, self.__current_log, audio))
        self.__reset()

    # Function called in a loop, representing the effect of time on the system
    # In this function all subsistems' dynamic state are "advanced through time"
    def time(self):
        done = True
        try:
            # The motor phoneme program is executed
            done, newState = self.__mpp.time(self.__vt.getState())  # raises ValueError
            # The results are logged
            self.__current_log.append(newState)
            self.__targets_log.append(self.__mpp.getCurrentTarget())
            # Vocal tract is updated: this is the actual vocal tract movement
            self.__vt.setState(WorkingParList(newState))
            # End of the utterance
            if done:
                if self.__displayPlot:
                    self.__plot().show()
                self.speak()
        except ValueError as e:
            self.__bucket.put((True, "An error has been encountered while executing " +
                               self.__current_utterance + ':\n' + str(e)))
        return done  # This is needed when command switch is external (e.g. for testing purposes)

    # Safely kills the thread
    def kill(self):
        self.__kill.set()

    # Run method for the thread
    def run(self):
        safe = 0
        while self.__live():
            if self.__current_utterance:
                self.__safeTime(safe)
                safe += 1
            else:
                self.__commandSwitch()
                safe = 0
        # This is needed because of the c_types in the api
        if self.__vt:
            self.__vt.close()


# TODO: write tests
