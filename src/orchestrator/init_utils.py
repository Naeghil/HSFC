# -------------------------------------------------------------------------------
# Name:        init_utils
# Purpose:     Utility functions used in the initialization of the orchestrator
#
# Author:      Roberto Sautto
#
# Last mod:    07/04/2020
# Copyright:   (c) Roberto Sautto 2020
# Licence:     <your licence>
# -------------------------------------------------------------------------------

# Global imports
import os
import sys
# Local imports
from src.utils.utils import extractFileInfo
import src.utils.paramlists as PL
from src.vtract.expose import Synthesizer


# Loads the configuration file, assuming it's not been moved
def loadConfig(path):
    c_info = extractFileInfo(path+os.sep+'config')  # Raises FileNotFound
    if c_info is None:
        print('Loading configuration failed.')
        sys.exit()
    # HARDCODED
    ext = '.dll' if sys.platform == 'win32' else '.so'
    conf = {'path': path,  # Path to the root of the application
            'apipath':  # Full path to the VTLAPI
                path + c_info[1] + 'VocalTractLabApi' + c_info[0] + ext,
            'speaker':  # Full path to the speaker file
                path + c_info[1] + c_info[2],
            'frate': int(c_info[3]),  # The frame rate
            'qred': int(c_info[4]),  # The quality reduction
            'err': float(c_info[5])}  # Maximum achievable error
    return conf


# Pre-initialization configuration, initializes certain class variables
def preliminaryInitialization(path, details):
    print('Loading configuration...')
    conf = loadConfig(path)  # Raises FileNotFound
    # Even though this is not a configuration, the api requires
    # to be initialized before parameters information can be extracted
    print('Initializing syntesizer...')
    synthesizer = Synthesizer(conf['apipath'], conf['speaker'], conf['frate'], conf['qred'])
    if details: synthesizer.display()
    print('Loading parameters information...')
    param_info = synthesizer.getParametersInfo()
    if details: param_info.display()
    print('  Initializing parameters lists...')
    PL.ParList.setIndexes(param_info.vlabels + param_info.glabels, param_info.working_labels)
    PL.State.validate = param_info.validate
    return conf, synthesizer, param_info
