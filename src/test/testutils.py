# -------------------------------------------------------------------------------
# Name:        testutils
# Purpose:     Utilities to write tests
#
# Author:      Roberto Sautto
#
# Last mod:    9/04/2020
# Copyright:   (c) Roberto Sautto 2020
# Licence:     <your licence>
# -------------------------------------------------------------------------------

# Global imports
import random
import string


# Generating random 2-letter labels for our parameters
def generate_parameter_labels():
    par_no = random.randrange(1, 30)
    par_labels = []
    while len(par_labels) != par_no:
        new = random.choice(string.ascii_lowercase) + \
              random.choice(string.ascii_lowercase)  # two-letter labels
        if new not in par_labels:
            par_labels.append(new)
    return par_labels


# Defining random maximum and minimum bounds for the parameters
def generate_parameter_bounds(parameter_labels):
    mins = {}
    maxs = {}
    for label in parameter_labels:
        v1 = random.triangular(-10.0, 10.0)
        v2 = random.triangular(-10.0, 10.0)
        mins[label] = min(v1, v2)
        maxs[label] = max(v1, v2)
    return mins, maxs
