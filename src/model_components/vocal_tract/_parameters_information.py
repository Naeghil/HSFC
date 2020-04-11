# -------------------------------------------------------------------------------
# Name:        parameters_information
# Purpose:     Databag for information about the parameters of the synthesizer
#
# Author:      Roberto Sautto
#
# Created:     04/03/2020
# Copyright:   (c) Roberto Sautto 2020
# Licence:     <your licence>
# -------------------------------------------------------------------------------

# Global imports
import copy
import ctypes


# This assumes vt and glottis parameters have different names
class VTParametersInfo:
    # Class variables
    _glabels = []
    _vlabels = []
    # Working labels are the ones actually used for motion
    _working_labels = []  # vlabels + pressure + lower_rest_displacement + upper_rest_displacement + f0

    def __init__(self, vt, vtp_no, gp_no):
        self._mins = {}  # Minimum values the articulator parameters can take
        self._defs = {}  # Default or "rest" values
        self._maxs = {}  # Maximum values the articulator parameters can take

        # Types for the api
        TRACT_PARAM_TYPE = ctypes.c_double * vtp_no
        GLOTTIS_PARAM_TYPE = ctypes.c_double * gp_no

        # Vocal tract parameters
        tract_param_names = ctypes.c_char_p((' ' * 32 * vtp_no).encode())
        tract_param_min = TRACT_PARAM_TYPE()
        tract_param_max = TRACT_PARAM_TYPE()
        tract_param_neutral = TRACT_PARAM_TYPE()

        # Extract vocal tract parameters information
        vt.vtlGetTractParamInfo(tract_param_names, ctypes.byref(tract_param_min),
                                ctypes.byref(tract_param_max), ctypes.byref(tract_param_neutral))
        # Store labels in the appropriate class variables
        VTParametersInfo._vlabels = tract_param_names.value.decode().split()
        VTParametersInfo._working_labels.extend(VTParametersInfo._vlabels)

        # Save vocal tract parameters information
        vtp_max = list(tract_param_max)
        vtp_min = list(tract_param_min)
        vtp_def = list(tract_param_neutral)
        for i in range(len(VTParametersInfo._vlabels)):
            l = VTParametersInfo._vlabels[i]
            self._mins[l] = vtp_min[i]
            self._defs[l] = vtp_def[i]
            self._maxs[l] = vtp_max[i]

        # Glottis parameters
        glottis_param_names = ctypes.c_char_p((' ' * 32 * gp_no).encode())
        glottis_param_min = GLOTTIS_PARAM_TYPE()
        glottis_param_max = GLOTTIS_PARAM_TYPE()
        glottis_param_neutral = GLOTTIS_PARAM_TYPE()

        # Extract glottis parameters information
        vt.vtlGetGlottisParamInfo(glottis_param_names, ctypes.byref(glottis_param_min),
                                  ctypes.byref(glottis_param_max), ctypes.byref(glottis_param_neutral))

        # Store labels in the appropriate class variables
        VTParametersInfo._glabels = glottis_param_names.value.decode().split()
        VTParametersInfo._working_labels.extend(
            ['pressure', 'lower_rest_displacement', 'upper_rest_displacement', 'f0'])

        # Save glottis parameters information
        g_max = list(glottis_param_max)
        g_min = list(glottis_param_min)
        g_def = list(glottis_param_neutral)
        for i in range(len(VTParametersInfo._glabels)):
            l = VTParametersInfo._glabels[i]
            self._mins[l] = g_min[i]
            self._defs[l] = g_def[i]
            self._maxs[l] = g_max[i]
        # Pressure adjustment:
        self._defs['pressure'] = 0.0

    # Getters:
    @staticmethod
    def getWorkingLabels():
        return copy.deepcopy(VTParametersInfo._working_labels)

    @staticmethod
    def getVocalLabels():
        return copy.deepcopy(VTParametersInfo._vlabels)

    @staticmethod
    def getGlottalLabels():
        return copy.deepcopy(VTParametersInfo._glabels)

    def getDefaults(self):
        return copy.deepcopy(self._defs)

    # This function validates the new value of parameter 'key' when updating the state of the vocal tract
    def validate(self, key: str, new: float) -> float:
        if new < self._mins[key]:
            return self._mins[key]
        if new > self._maxs[key]:
            return self._maxs[key]
        return new

    # This function "lowers" the expectation for a target by limiting it to its maxima and minima
    # NOTE: it assumes a np.array of len(_working_labels)
    def sanitize_parameter_list(self, parameter_list):
        sanitized = []
        for i in range(len(VTParametersInfo._working_labels)):
            label = VTParametersInfo._working_labels[i]
            sanitized.append(self.validate(label, parameter_list[i]))
        return sanitized

    # Displays information to the user
    def display(self):
        print('    Parameters as Label(min/def/max):')
        vt_info = list(k+'('+str(self._mins[k])+'/'+str(self._defs[k])+'/'+str(self._maxs[k])+')  '
                       for k in VTParametersInfo._vlabels)
        g_info = list(k+'('+str(self._mins[k])+'/'+str(self._defs[k])+'/'+str(self._maxs[k])+')  '
                      for k in ['pressure', 'f0', 'upper_rest_displacement', 'lower_rest_displacement'])
        print(' '.join(vt_info))
        print(' '.join(g_info))


# Definitions for interface purposes:
def getWorkingLabels():
    return VTParametersInfo.getWorkingLabels()


def getVocalLabels():
    return VTParametersInfo.getVocalLabels()


def getGlottalLabels():
    return VTParametersInfo.getGlottalLabels()
