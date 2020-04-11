# -------------------------------------------------------------------------------
# Name:        test_parlist
# Purpose:     Tests for critical methods in utils.parlists.py
#              The functions to be tested are: State.update()
#
# Author:      Roberto Sautto
#
# Last mod:    9/04/2020
# Copyright:   (c) Roberto Sautto 2020
# Licence:     <your licence>
# -------------------------------------------------------------------------------

# State.update() is meant to safely update the state object so that parameters don't
# exceed the maximum value allowed nor go below the minimum value allowed.
# This is achieved through a State.validate() function, which during execution
# actually points to VTParametersInfo.validate()

# Global imports
import random
# Local imports
from ..model_components._parameters_lists import State, ParList
from . import testutils


# Four equivalence classes: overshoot, undershoot, in range, on boundary
def generate_cases(parameter_labels, mins, maxs):
    test_cases = []  # element format: (label, input, expected output)
    for i in range(25):
        lab = random.choice(parameter_labels)
        test_cases.append((
            lab,
            random.triangular(-10, mins[lab]),
            mins[lab]))  # Undershoot. Expected behaviour: choose the minimum
        lab = random.choice(parameter_labels)
        inp = random.triangular(mins[lab], maxs[lab])
        test_cases.append((lab, inp, inp))  # In range. Expected behaviour: use the new value
        lab = random.choice(parameter_labels)
        test_cases.append((
            lab,
            random.triangular(maxs[lab], 10.0),
            maxs[lab]))  # Overshoot. Expected behaviour: choose the maximum
        lab = random.choice(parameter_labels)
        which = random.choice([maxs, mins])
        test_cases.append((lab, which[lab], which[lab]))  # On boundary. Expected behaviour: choose the boundary
    return test_cases


def test_update():
    # Prepping:
    random.seed()
    # Simulating execution environment:
    # because they are configurable externally, these values are randomly generated
    parameter_labels = testutils.generate_parameter_labels()
    mins, maxs = testutils.generate_parameter_bounds(parameter_labels)
    # Setting up ParList's dictionaries
    ParList.setIndexes(parameter_labels, parameter_labels)

    # Mirroring VTParametersInfo.validate()
    def validate(k: str, val: float) -> float:
        if val < mins[k]:
            return mins[k]
        if val > maxs[k]:
            return maxs[k]
        return val
    State.setValidationFunction(validate)
    state = State()  # Create a zero-list state
    for case in generate_cases(parameter_labels, mins, maxs):
        key = case[0]
        new = case[1]
        expected = case[2]
        state.update(key, new)
        assert state.get(key) == expected, "Failed with key="+str(key)+", new="+str(new)+", expected="+str(expected)
