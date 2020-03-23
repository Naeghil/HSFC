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
import numpy as np
from abc import abstractmethod

from src.vtract.paraminfo import VTParametersInfo as PI


# This is not meant to be used on its own
class ParList(object):
    _wl_indexes = {}  # Used to index the internal representation for all parameters
    _al_indexes = {}  # Used to index the internal representation for working parameters

    @staticmethod
    def setIndexes(all_labels, working_labels):
        ParList.__al_indexes = {all_labels[idx]: idx for idx in len(all_labels)}
        ParList.__wl_indexes = {working_labels[idx]: idx for idx in len(working_labels)}

    @abstractmethod
    def __init__(self):
        pass

    def _init(self, idxs, init=None):
        self._idx = idxs
        req_par = len(idxs)
        if init is None:  # Zero full-list
            self._parameters = np.array([0.0]*req_par)
        elif isinstance(init, ParList) and \
                len(init._parameters) == req_par:
            self._parameters = np.array(init._parameters, dtype='f8')
        elif isinstance(init, (np.ndarray, list)) and \
                len(init) == req_par:
            self._parameters = np.array(init, dtype='f8')
        else:
            raise Exception("Wrong initialization arguments")

    def get(self, k):
        idx = self._idx.get(k, None)
        return self._parameters[idx] if idx else None

    def asString(self):
        info = list(k + '=' +
                    str(round(self._parameters[self._idx[k]], 6))
                    for k in self._idx.keys())
        return ' '.join(info)

    def update(self, k, value):
        idx = self._idx.get(k, None)
        if idx: self._parameters[idx] = value


# A State must have all the parameters, as it must be converted to a frame
class State(ParList):
    def __init__(self, init=None):
        super(State, self).__init__()
        super(State, self)._init(super()._al_indexes, init)

    def asFrame(self):
        idx = super(State, self)._idx
        v = list(super(State, self)._parameters[idx[k]] for k in PI.vlabels)
        g = list(super(State, self)._parameters[idx[k]] for k in PI.glabels)
        return [v, g]

    def update(self, k, value: float):
        idx = self._idx.get(k, None)
        if idx: self._parameters[idx] = PI.validate(k, value)


class WorkingParList(ParList):
    @abstractmethod
    def __init__(self, init):
        super(WorkingParList, self).__init__()
        super(WorkingParList, self)._init(super(WorkingParList, self)._wl_indexes, init)


class Velocity(WorkingParList):
    def __init__(self, init=None):
        super(Velocity, self).__init__(init)


class Target(WorkingParList):
    def __init__(self, t_constant, init=None):
        super(Target, self).__init__(init)
        self.effort = -1/t_constant

    def makeNonPhonatory(self, t_constant):
        pp = Target(t_constant, self)
        super(Target, pp).update('pressure', 0.0)
