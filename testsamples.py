# -------------------------------------------------------------------------------
# Name:        test_samples
# Purpose:     Part of system testing. This performs an equivalence partitioning
#              test on the entire system.
#
# Author:      Naeghil
#
# Last mod:    9/04/2020
# Copyright:   (c) Naeghil 2020
# Licence:     <your licence>
# -------------------------------------------------------------------------------

# Local imports
from src.utils import extractFileInfo
from main import main

# In this script, acceptable arguments for 'say' are considered, and samples
# for the experiment are synthesized.
if __name__ == '__main__':

    inp = list('say '+sample for sample in extractFileInfo('resources/samples/kept candidates.txt'))
    main(inp)
