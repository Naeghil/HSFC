# -------------------------------------------------------------------------------
# Name:        test_motion
# Purpose:     Tests for critical methods for the motion of the articulators.
#              The functions to be tested are: MotorPhonemePrograms.time(), VocalTract.time()
#
# Author:      Roberto Sautto
#
# Last mod:    9/04/2020
# Copyright:   (c) Roberto Sautto 2020
# Licence:     <your licence>
# -------------------------------------------------------------------------------

# MotorPhonemePrograms is meant to move the vocal tract over its trajectory
# by following a given plan. VocalTract models the human vocal tract through
# its parameters, which represent the position of a number of articulators.
# While MotorPhonemePrograms.time() drives a sort of "motor impulse",
# VocalTract.time() executes the "physical consequences" of that impulse.
# The inputs tested here are therefore the targets that the motion aims towards.
# Equivalence classes are: acceptable targets, unreachable targets, no targets
# Success of this test is also given by visual inspection of the plot produced
# NOTE: this is a convenient way to test the generic behaviour of Orchestrator.time()
# and was used in its development

# Global imports
import random
import numpy as np
import matplotlib.pyplot as pl
# Local imports
from ..model_components.phonological_level import MotorPhonemePrograms
from . import testutils
from ..model_components._parameters_lists import ParList, Target, WorkingParList, State
from ..model_components.vocal_tract import VocalTract


class MockSynth:
    def __init__(self):
        pass

    # This is the method used by VocalTract.time(),
    # see synthesizer.Synthesizer for the original
    def dump(self, state):
        pass


# There seems to be a caching issue with parameter_list, so this is needed:
class MockParInfo:
    parameter_labels = []
    mins = {}
    maxs = {}

    def __init__(self):
        pass

    @staticmethod
    def setParInfo(parameter_labels, mins, maxs):
        MockParInfo.parameter_labels = parameter_labels
        MockParInfo.mins = mins
        MockParInfo.maxs = maxs

    @staticmethod
    def mock_expected(parameter_list):
        return sanitize_parameter_list(parameter_list, MockParInfo.parameter_labels, MockParInfo.mins, MockParInfo.maxs)

    @staticmethod
    def validate(k: str, val: float) -> float:
        if val < MockParInfo.mins[k]:
            return MockParInfo.mins[k]
        if val > MockParInfo.maxs[k]:
            return MockParInfo.maxs[k]
        return val


def plot(states_log, targets_log, parameter_labels, mins=None, maxs=None):
    toPlot = np.array(states_log).T
    targets = np.array(targets_log).T

    figure = pl.figure()
    par_no = toPlot.shape[0]
    for i in range(par_no):
        subplot = figure.add_subplot(6, 5, i + 1)
        subplot.set_title(parameter_labels[i])
        subplot.plot(toPlot[i], 'b')  # State in blue
        subplot.plot(targets[i], 'g')  # Targets in green
        # Possible range in red
        if mins is not None:
            subplot.plot([mins[parameter_labels[i]]]*toPlot.shape[1], 'r')
        if maxs is not None:
            subplot.plot([maxs[parameter_labels[i]]]*toPlot.shape[1], 'r')

    pl.subplots_adjust(left=0.05, right=0.99, top=0.95, bottom=0.05, hspace=1.0)
    return pl


# Generate a list of parameters comprised between their respective maxima and minima
def generate_parameter_list(parameter_labels, min_vals=None, max_vals=None):
    if min_vals is None:
        min_vals = {label: -10.0 for label in parameter_labels}
    if max_vals is None:
        max_vals = {label: 10.0 for label in parameter_labels}
    parameter_list = np.array(list(random.triangular(min_vals[label], max_vals[label])
                                   for label in parameter_labels), dtype='f8')
    return parameter_list


# This function has essentially been tested in test_parlist.py
def sanitize_parameter_list(parameter_list, parameter_labels, mins, maxs):
    sanitized = []
    for i in range(len(parameter_labels)):
        label = parameter_labels[i]
        if parameter_list[i] > maxs[label]:
            sanitized.append(maxs[label])
        elif parameter_list[i] < mins[label]:
            sanitized.append(mins[label])
        else:
            sanitized.append(parameter_list[i])
    return sanitized


# Each case is (target, expected reaching, expected behaviour)
def generate_cases(parameter_labels, mins, maxs):
    test_cases = []

    for i in range(20):
        # Reachable targets
        target = generate_parameter_list(parameter_labels, mins, maxs)
        test_cases.append((Target(10.0, target),
                           target,
                           "Reach the target as it is."))
        # Potentially unreachable targets
        target = generate_parameter_list(parameter_labels)
        test_cases.append((Target(10.0, target),
                           sanitize_parameter_list(target, parameter_labels, mins, maxs),
                           "Stop certain targets as they reach their boundary"))
    return test_cases


def test_no_target():
    # Prepping:
    state_log = []  # Logs states achieved by the command
    target_log = []  # Logs targets to achieve at a certain time

    # Simulating execution environment
    parameter_labels = testutils.generate_parameter_labels()
    mins, maxs = testutils.generate_parameter_bounds(parameter_labels)
    ParList.setIndexes(parameter_labels, parameter_labels)
    MockParInfo.setParInfo(parameter_labels, mins, maxs)
    State.setValidationFunction(MockParInfo.validate)
    # VTParametersInfo hasn't been set (see _parameters_lists.py)
    State.asTargetParameters = WorkingParList.asTargetParameters
    MotorPhonemePrograms.setSanitizingFunction(MockParInfo.mock_expected)

    # Initialize items to test
    initial_state = generate_parameter_list(parameter_labels, mins, maxs)  # Generate random initial state
    mpp = MotorPhonemePrograms(initial_state)
    vt = VocalTract(MockSynth(), 1, initial_state)

    # Testing the "no target" equivalence class
    # Expected behaviour: no movement
    for _ in range(500):
        done, new = mpp.time(vt.getState())
        vt.time(WorkingParList(new), parameter_labels)
        state_log.append(vt.getState())
        target_log.append(initial_state)
    plot(state_log, target_log, parameter_labels).show()
    assert (vt.getState() == initial_state).all()


def test_motion():
    # Prepping:
    state_log = []  # Logs states achieved by the command
    target_log = []  # Logs targets to achieve at a certain time

    # Simulating execution environment
    parameter_labels = testutils.generate_parameter_labels()
    mins, maxs = testutils.generate_parameter_bounds(parameter_labels)
    ParList.setIndexes(parameter_labels, parameter_labels)
    MockParInfo.setParInfo(parameter_labels, mins, maxs)
    State.setValidationFunction(MockParInfo.validate)
    # VTParametersInfo hasn't been set (see _parameters_lists.py)
    State.asTargetParameters = WorkingParList.asTargetParameters
    MotorPhonemePrograms.setSanitizingFunction(MockParInfo.mock_expected)

    # Initialize items to test
    initial_state = generate_parameter_list(parameter_labels, mins, maxs)  # Generate random initial state
    mpp = MotorPhonemePrograms(initial_state)
    vt = VocalTract(MockSynth(), 1, initial_state)
    # Run tests:
    for case in generate_cases(parameter_labels, mins, maxs):
        mpp.addPlan([case[0]])
        mpp.time(vt.getState())  # Prompt mpp to advance to the new state
        done = False
        counter = 0
        while not done and counter < 500:
            done, new = mpp.time(vt.getState())
            vt.time(WorkingParList(new), parameter_labels)
            state_log.append(vt.getState())
            target_log.append(case[1])
            counter += 1
        assert counter != 500, "Timeout while producing: "+str(case[0])
        #plt = plot(state_log, target_log, parameter_labels, mins, maxs)
        #plt.show(block=True)
        state_log = []
        target_log = []
        error = np.square(vt.getState() - case[1]).mean()
        # 0.04 is the maximum error after which a target is considered reached
        assert error <= 0.04, case[2] + " Reached: "+str(vt.getState()) + ". Expected: "+str(case[1])
