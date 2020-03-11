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
    working_labels = []  # Labels that are actually used for motion

    def __init__(self, init=None):
        self.__parameters = {}
        if init is None:
            for key in self.vlabels+self.glabels:
                self.__parameters[key] = 0.0
        elif isinstance(init, dict):
            for key in self.vlabels+self.glabels:
                self.__parameters[key] = init.get(key, 0.0)
        elif isinstance(init, ParList):
            self.__parameters = init.__getParameters()

    def __getParameters(self):
        return copy.deepcopy(self.__parameters)

    def get(self, k):
        return self.__parameters.get(k, None)

    def asString(self):
        info = list(k + '=' + str(round(self.__parameters[k], 6)) for k in self.working_labels)
        return ' '.join(info)

    def update(self, k, value):
        if k in self.working_labels:
            self.__parameters[k] = value


class State(ParList):
    def __init__(self, init=None):
        super().__init__(init)

    def asFrame(self):
        g = list(self.get(k) for k in self.glabels)
        v = list(self.get(k) for k in self.vlabels)
        return [v, g]


class Velocity(ParList):
    def __init__(self, init=None):
        if init and isinstance(init, dict):
            d = init.pop('d_rest', None)
            if d:
                init['upper_rest_displacement'] = d
                init['lower_rest_displacement'] = d
        super().__init__(init)

    def get(self, k):
        if k == 'd_rest': k = 'upper_rest_displacement'
        return super().get(k)
    
    def update(self, k, value):
        if k == 'd_rest':
            super().update('upper_rest_displacement', value)
            super().update('lower_rest_displacement', value)
        else:
            super().update(k, value)


# TODO: rework this
class Target(Velocity):
    def __init__(self, time, init=None, mask=None):
        self.__activation = 0.0  # Activation of the target
        self.__mask = {}  # Relative importance of the targets

        if isinstance(init, list):
            pass
        else:
            super().__init__(init)
        if mask is None:
            mask = {k:1.0 for k in super().working_labels}
        for k in super().working_labels:
            self.__mask[k] = mask[k]

    # Targets are static cause no learning for now
    def update(self, k, value):
        pass
