# -------------------------------------------------------------------------------
# Name:        paramlists
# Purpose:     useful wrappers for parameters
#
# Author:      Roberto Sautto
#
# Created:     04/03/2020
# Copyright:   (c) Roberto Sautto 2020
# Licence:     <your licence>
# -------------------------------------------------------------------------------
import copy


class ParList:
    glabels = []  # Glottis labels of the parameters for the synthesizer
    vlabels = []  # Vocal labels of the parameters for the synthesizer
    working_labels = [] # Labels that are actually used for motion

    def __init__(self, init=None):
        self.__parameters = {}
        if init is None:
            for key in self.vlabels+self.glabels:
                self.__parameters[key] = 0.0
        elif isinstance(init, dict):
            for key in self.vlabels+self.glabels:
                self.__parameters[key] = init[key]
        elif isinstance(init, ParList):
            self.__parameters = init.__getParameters()

    def __getParameters(self):
        return copy.deepcopy(self.__parameters)

    def get(self, k):
        return self.__parameters[k]

    def asString(self):
        info = list(k+'='+str(self.__parameters[k]) for k in self.working_labels)
        return ' '.join(info)


class State(ParList):
    def __init__(self, init=None):
        ParList.__init__(self, init)

    def asFrame(self):
        g = list(self._ParList__parameters[k] for k in self.glabels)
        v = list(self._ParList__parameters[k] for k in self.vlabels)
        return [v, g]
