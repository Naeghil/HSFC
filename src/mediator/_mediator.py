# -------------------------------------------------------------------------------
# Name:        mediator
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
from queue import Empty, Queue
import numpy as np
from matplotlib import pyplot as pl
# Local imports:
from . import _init_utils as init
from ..model_components import WorkingParList, getWorkingLabels
from ..utils import UnrecoverableException, RecoverableException, HSFCThread


class Mediator(HSFCThread):
    def __init__(self, production_queue: Queue,  # Input to the mediator
                 results_queue: Queue):  # Output from the mediator
        super(Mediator, self).__init__(production_queue, results_queue)

        # Loading configurations and pre-initialization:
        try:
            # raises FileNotFound, unrecoverable:
            conf, synth, self.param_info = init.preliminary_initialization()
        except Exception as e:
            raise UnrecoverableException('Loading configuration failed: \n  '+str(e))

        # Components initialization:
        try:
            self._spt, self._msp, self._vt, self._mpp = \
                init.component_initialization(conf, synth, self.param_info)
        except Exception as e:
            raise UnrecoverableException('Initialization failed: \n  '+str(e))
            if self._vt:
                self._vt.close()

        # Logging variables
        self._current_utterance = None
        self._current_log = []  # Temporary storage for logs
        self._targets_log = []  # Temporary storage for logs
        # Other variables
        self._toPlot = False  # If true, each utterance will be plotted before being synthesized
        self._max_time_letter = int(conf['frate']/2)  # Maximum frames allowed per character (0.5s)

    # Moves on to the next command if available, otherwise it waits
    def _command_switch(self):
        try:
            # Extract next utterance
            self._toPlot, self._current_utterance = self._input.get(timeout=1)
            self._input.task_done()
            try:
                # Plan for next utterance
                plan = self._msp.makePlan(self._current_utterance)  # raises RecoverableException
                # Adds utterance to plan, creating the appropriate motor commands
                self._mpp.addPlan(plan)  # raises UnrecoverableException
            except UnrecoverableException as e:
                self._output.put(("terminate", "An error has been encountered while planning for " +
                                   self._current_utterance+':\n  '+str(e)))
                self._kill.set()
            except RecoverableException as e:
                self._output.put(("message", "Unable to plan for " + self._current_utterance +
                                   " because:\n  "+str(e)))
                self._current_utterance = None  # Skip the utterance
        except Empty:
            pass  # This is only needed in case the user terminates the program while in wait

    # Merely a wrapper for the time function to avoid clogging the run() method
    def _safe_time(self, safe):
        # Gives 0.5 seconds per letter, +0.5 seconds (for initial and final targets), which is more than enough
        if safe > len(self._current_utterance)+1 * self._max_time_letter:
            self._output.put(("message",
                               "The current command for " + self._current_utterance +
                               " has been reset because of timeout"))
            self._reset()
            self._vt.speak(self._current_utterance)  # This flushes the synthesizer; it's unknown if it may get stuck
        else:
            self.time()

    # Resets logging variables
    def _reset(self):
        self._current_log = []
        self._targets_log = []
        self._current_utterance = None

    # This function creates a plot of the vocal tract state, including its targets
    def _plot(self):
        # HARDCODED
        toPlot = np.array(self._current_log).T
        targets = np.array(self._targets_log).T
        labels = np.array(getWorkingLabels())
        # Some indexes are removed because they don't seem to contribute to production
        rem_idxs = [21, 22, 23, 27]
        toPlot = np.delete(toPlot, rem_idxs, axis=0)
        targets = np.delete(targets, rem_idxs, axis=0)
        labels = np.delete(labels, rem_idxs, axis=0)

        figure, subplots = pl.subplots(6, 4)
        for i in range(6):
            for k in range(4):
                subplots[i][k].plot(toPlot[4*i+k], 'b')  # State in blue
                subplots[i][k].plot(targets[4*i+k], 'g')  # Targets in green
                subplots[i][k].set_title(labels[4*i+k])

        figure.suptitle(self._current_utterance)
        pl.subplots_adjust(left=0.05, right=0.99, top=0.90, bottom=0.05, hspace=1.0)
        return pl

    # Once a motor plan has been executed, the utterance is synthesized and its data is logged and flushed
    # At the end, the system is ready for a new word
    def speak(self):
        self._vt.speak(self._current_utterance)
        self._output.put(('message', "'" + self._current_utterance + "' has been synthesized"))
        self._reset()

    # Function called in a loop, representing the effect of time on the system
    # In this function all subsistems' dynamic state are "advanced through time"
    def time(self):
        done = True  # If an unrecoverable exception is thrown
        try:
            # The motor phoneme program is executed
            done, newState = self._mpp.time(self._vt.getState())  # raises UnrecoverableException
            # The results are logged
            self._current_log.append(newState)
            self._targets_log.append(self._mpp.getCurrentTarget())
            # Vocal tract is updated: this is the actual vocal tract movement
            self._vt.time(WorkingParList(newState))  # raises UnrecoverableException
            # End of the utterance
            if done:
                if self._toPlot:
                    self._plot().show()
                self.speak()
        except UnrecoverableException as e:
            self._output.put(("termination", "An error has been encountered while executing " +
                               self._current_utterance + ':\n' + str(e)))
            self._kill.set()
        return done  # This is needed when command switch is external (e.g. for testing purposes)

    # Run method for the thread
    def run(self):
        safe = 0
        while self.live():
            if self._current_utterance:
                self._safe_time(safe)
                safe += 1
            else:
                self._command_switch()
                if self._current_utterance:
                    self._output.put(("message", "Started production of '" + self._current_utterance + "'"))
                safe = 0
        # This is needed because of the c_types in the api
        if self._vt:
            self._vt.close()
