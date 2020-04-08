# -------------------------------------------------------------------------------
# Name:        paramlists
# Purpose:     Useful wrappers for parameters. Some were meant to have
#              more complex interactions with the system, but are now being used
#              as safe databages for articulator parameters
#
# Author:      Roberto Sautto
#
# Last mod:     07/04/2020
# Copyright:   (c) Roberto Sautto 2020
# Licence:     <your licence>
# -------------------------------------------------------------------------------

# Golbal imports
import numpy as np
from abc import abstractmethod
# Local imports
from src.utils.utils import UnrecoverableException
from src.vtract.paraminfo import VTParametersInfo as PI


# This is an abstract class
class ParList(object):
    # The internal representation is an np.array,
    # so there needs to be a conversion between parameter label and index
    _wl_indexes = {}  # Used to index the internal representation for all parameters
    _al_indexes = {}  # Used to index the internal representation for working parameters

    # Used to set the indexingg variables
    @staticmethod
    def setIndexes(all_labels, working_labels):
        print(working_labels)
        ParList._al_indexes = {all_labels[idx]: idx for idx in range(len(all_labels))}
        ParList._wl_indexes = {working_labels[idx]: idx for idx in range(len(working_labels))}

    @abstractmethod
    def __init__(self):
        pass

    # non-constructor initialization
    def _init(self, idxs: dict, init=None):
        # The set of parameter names used by the specific subclass,
        # this is essentially a reference to one of the class dictionaries
        self._idx = idxs
        req_par = len(idxs)  # The number of required parameters
        # zero-list originally meant for initial velocity of the system
        if init is None:  # Zero full-list
            self._parameters = np.array([0.0]*req_par)
        # Construct a parameter list from another one
        elif isinstance(init, ParList) and \
                len(init._parameters) == req_par:
            self._parameters = np.array(init._parameters, dtype='f8')
        # Construct a parameter list from np.array or list
        elif isinstance(init, (np.ndarray, list)) and \
                len(init) == req_par:
            self._parameters = np.array(init, dtype='f8')
        else:
            # Cannot construct a parameter list from any other data type
            raise UnrecoverableException("The parameters list object could not be initialized. This is a bug.")

    # Returns the requested parameter, if exists
    def get(self, k, default=0.0):
        idx = self._idx.get(k, None)
        return self._parameters[idx] if idx else default

    # Returns a copy of only the working parameters, independently of the subclass
    def asTargetParameters(self):
        return np.array(list(self._parameters[self._idx[k]] for k in PI.working_labels), 'f8')

    # This is a "safe" update of a parameter (if they're not in the object, they are not added)
    def update(self, k, value):
        idx = self._idx.get(k, None)
        if idx: self._parameters[idx] = value


# A State must have all the parameters, as can be converted to a frame
class State(ParList):
    validate = None  # Validation function, from paraminfo

    def __init__(self, init=None):
        super(State, self).__init__()
        super(State, self)._init(self._al_indexes, init)  # raises UnrecoverableException

    # Returns a the vocal tract and glottal frames, as required by the api
    def asFrame(self):
        idx = self._idx
        v = list(self._parameters[idx[k]] for k in PI.vlabels)
        g = list(self._parameters[idx[k]] for k in PI.glabels)
        return [v, g]

    # Since this is the vocal tract state, its parameters must be validated for minimum and maximum values
    def update(self, k, value: float):
        super(State, self).update(k, self.validate(k, value))


# Helper class for parameter lists only requiring working parameters
class WorkingParList(ParList):
    def __init__(self, init):
        super(WorkingParList, self).__init__()
        # raises UnrecoverableException:
        super(WorkingParList, self)._init(super(WorkingParList, self)._wl_indexes, init)

    # No need to check (see superclass)
    def asTargetParameters(self):
        return np.array(self._parameters)


# This was meant to be used with the original motor control (see MPP), but now States are set directly
class Velocity(WorkingParList):
    def __init__(self, init=None):
        super(Velocity, self).__init__(init)  # raises UnrecoverableException


# A target has not only a parameter list, but also an "effort"
class Target(WorkingParList):
    def __init__(self, t_constant, init=None):
        super(Target, self).__init__(init)  # raises UnrecoverableException
        # As specified in Birkholz's paper. Used for MotorCommand calculations:
        self.__effort = -1/t_constant

    def getEffort(self):
        return self.__effort

    def makeNonPhonatory(self, t_constant):
        pp = Target(t_constant, self)
        super(Target, pp).update('pressure', 0.0)
        return pp

# TODO: make tests
