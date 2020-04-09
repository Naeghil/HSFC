# -------------------------------------------------------------------------------
# Name:        paraminfo
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
    __glabels = []
    __vlabels = []
    # Working labels are the ones actually used for motion
    __working_labels = []  # vlabels + pressure + lower_rest_displacement + upper_rest_displacement + f0

    def __init__(self, vt, vtp_no, gp_no):
        self.__mins = {}  # Minimum values the articulator parameters can take
        self.__defs = {}  # Default or "rest" values
        self.__maxs = {}  # Maximum values the articulator parameters can take

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
        VTParametersInfo.__vlabels = tract_param_names.value.decode().split()
        VTParametersInfo.__working_labels.extend(VTParametersInfo.__vlabels)

        # Save vocal tract parameters information
        vtp_max = list(tract_param_max)
        vtp_min = list(tract_param_min)
        vtp_def = list(tract_param_neutral)
        for i in range(len(VTParametersInfo.__vlabels)):
            l = VTParametersInfo.__vlabels[i]
            self.__mins[l] = vtp_min[i]
            self.__defs[l] = vtp_def[i]
            self.__maxs[l] = vtp_max[i]

        # Glottis parameters
        glottis_param_names = ctypes.c_char_p((' ' * 32 * gp_no).encode())
        glottis_param_min = GLOTTIS_PARAM_TYPE()
        glottis_param_max = GLOTTIS_PARAM_TYPE()
        glottis_param_neutral = GLOTTIS_PARAM_TYPE()

        # Extract glottis parameters information
        vt.vtlGetGlottisParamInfo(glottis_param_names, ctypes.byref(glottis_param_min),
                                  ctypes.byref(glottis_param_max), ctypes.byref(glottis_param_neutral))

        # Store labels in the appropriate class variables
        VTParametersInfo.__glabels = glottis_param_names.value.decode().split()
        VTParametersInfo.__working_labels.extend(['pressure', 'lower_rest_displacement', 'upper_rest_displacement', 'f0'])

        # Save glottis parameters information
        g_max = list(glottis_param_max)
        g_min = list(glottis_param_min)
        g_def = list(glottis_param_neutral)
        for i in range(len(VTParametersInfo.__glabels)):
            l = VTParametersInfo.__glabels[i]
            self.__mins[l] = g_min[i]
            self.__defs[l] = g_def[i]
            self.__maxs[l] = g_max[i]
        # Pressure adjustment:
        self.__defs['pressure'] = 0.0

    # Getters:
    @staticmethod
    def getWorkingLabels():
        return copy.deepcopy(VTParametersInfo.__working_labels)

    @staticmethod
    def getVocalLabels():
        return copy.deepcopy(VTParametersInfo.__vlabels)

    @staticmethod
    def getGlottalLabels():
        return copy.deepcopy(VTParametersInfo.__glabels)

    def getDefaults(self):
        return copy.deepcopy(self.__defs)

    # This function validates the new value of parameter 'key' when updating the state of the vocal tract
    def validate(self, key: str, new: float) -> float:
        if new < self.__mins[key]:
            return self.__mins[key]
        if new > self.__maxs[key]:
            return self.__maxs[key]
        return new

    # This function "lowers" the expectation for a target by limiting it to its maxima and minima
    # NOTE: it assumes a np.array of len(__working_labels)
    def sanitize_parameter_list(self, parameter_list):
        sanitized = []
        for i in range(len(VTParametersInfo.__working_labels)):
            label = VTParametersInfo.__working_labels[i]
            sanitized.append(self.validate(label, parameter_list[i]))
        return sanitized

    # Displays information to the user
    def display(self):
        print('    Parameters as Label(min/def/max):')
        vt_info = list(k+'('+str(self.__mins[k])+'/'+str(self.__defs[k])+'/'+str(self.__maxs[k])+')  '
                       for k in VTParametersInfo.__vlabels)
        g_info = list(k+'('+str(self.__mins[k])+'/'+str(self.__defs[k])+'/'+str(self.__maxs[k])+')  '
                      for k in ['pressure', 'f0', 'upper_rest_displacement', 'lower_rest_displacement'])
        print(' '.join(vt_info))
        print(' '.join(g_info))
