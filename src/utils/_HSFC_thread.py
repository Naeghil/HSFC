# -------------------------------------------------------------------------------
# Name:        HSFC_thread
# Purpose:     Superclass for the two thread components
#
# Author:      Naeghil
#
# Last mod:    9/04/2020
# Copyright:   (c) Naeghil 2020
# Licence:     <your licence>
# -------------------------------------------------------------------------------

# Global imports
from threading import Thread, Event
from queue import Queue


class HSFCThread(Thread):
    def __init__(self, input_queue: Queue, output_queue: Queue):
        super(HSFCThread, self).__init__()
        # Queues
        self._input = input_queue
        self._output = output_queue
        # Threading management:
        self._kill = Event()  # Controls the loop in run()

    # Checking function for run()
    def live(self):
        return not self._kill.isSet()  # The "not" is a mere readibility sugar

    # Safely kills the thread
    def kill(self):
        self._kill.set()
