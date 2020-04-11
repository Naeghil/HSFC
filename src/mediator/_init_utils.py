# -------------------------------------------------------------------------------
# Name:        init_utils
# Purpose:     Utility functions used in the initialization of the mediator
#
# Author:      Roberto Sautto
#
# Last mod:    07/04/2020
# Copyright:   (c) Roberto Sautto 2020
# Licence:     <your licence>
# -------------------------------------------------------------------------------

# Global imports
import sys
# Local imports
from ..model_components import MotorPhonemePrograms, SomatoPhonemeTargets, MotorSyllablePrograms
from ..model_components import Synthesizer, VocalTract
from ..model_components import setIndexes, setValidation
from ..utils import extractFileInfo


# Loads the configuration file, assuming it's not been moved
def load_config():
    c_info = extractFileInfo('resources/config')  # raises FileNotFound
    if c_info is None:
        print('Loading configuration failed.')
        sys.exit()
    # HARDCODED
    ext = '.dll' if sys.platform == 'win32' else '.so'
    conf = {'apipath':  # Full path to the VTLAPI
                '.'+c_info[1] + 'VocalTractLabApi' + c_info[0] + ext,
            'speaker':  # Full path to the speaker file
                '.'+c_info[1] + c_info[2],
            'audiopath':  # Relative path to the output folder
                c_info[3],
            'frate': int(c_info[4]),  # The frame rate
            'qred': int(c_info[5]),  # The quality reduction
            'err': float(c_info[6])}  # Maximum achievable error
    return conf


# Pre-initialization configuration, initializes certain class variables
def preliminary_initialization():
    print('Loading configuration...')
    conf = load_config()  # raises FileNotFound
    # Even though this is not a configuration, the api requires
    # to be initialized before parameters information can be extracted
    print('Initializing syntesizer...')
    synthesizer = Synthesizer(conf['apipath'], conf['speaker'], conf['frate'], conf['qred'])
    synthesizer.display()
    print('Loading parameters information...')
    param_info = synthesizer.getParametersInfo()
    param_info.display()
    print('  Initializing parameters lists and related methods...')
    setIndexes(param_info.getVocalLabels() + param_info.getGlottalLabels(), param_info.getWorkingLabels())
    setValidation(param_info.validate)
    MotorPhonemePrograms.setSanitizingFunction(param_info.sanitize_parameter_list)
    return conf, synthesizer, param_info


def component_initialization(conf, synth, param_info):
    print('Initializing submodules...')
    print('  Loading somatophoneme targets...')
    spt = SomatoPhonemeTargets(conf['err'])
    print('  Initializing motor planner...')
    msp = MotorSyllablePrograms(
        spt.targets, spt.vow_constants, spt.con_constants)
    print('  Initializing vocal tract...')
    vt = VocalTract(synth, conf['qred'], param_info.getDefaults(), conf['audiopath'])
    print('  Initializing motor controller...')
    s0 = vt.getState()
    # raises ValueError, unrecoverable:
    mpp = MotorPhonemePrograms(s0, conf['frate'], spt.err)
    return spt, msp, vt, mpp
