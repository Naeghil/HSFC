# -------------------------------------------------------------------------------
# Name:        paraminfo
# Purpose:     databag for information about the parameters of the synthesizer
#
# Author:      Roberto Sautto
#
# Created:     04/03/2020
# Copyright:   (c) Roberto Sautto 2020
# Licence:     <your licence>
# -------------------------------------------------------------------------------

import ctypes


# This assumes vt and glottis parameters have different names
class VTParametersInfo:
    def __init__(self, vt, vtp_no, gp_no):
        # Instance variables:
        self.__vt_names = []  # Ordered parameter names
        self.__g_names = []  # Ordered parameter names
        # These are usually consulted throught the previous two:
        self.__mins = {}
        self.__defs = {}
        self.__maxs = {}

        TRACT_PARAM_TYPE = ctypes.c_double * vtp_no
        GLOTTIS_PARAM_TYPE = ctypes.c_double * gp_no

        # Vocal tract parameters
        tract_param_names = ctypes.c_char_p((' ' * 32 * vtp_no).encode())
        tract_param_min = TRACT_PARAM_TYPE()
        tract_param_max = TRACT_PARAM_TYPE()
        tract_param_neutral = TRACT_PARAM_TYPE()
        print('1')
        # Extract vocal tract parameters information
        vt.vtlGetTractParamInfo(tract_param_names, ctypes.byref(tract_param_min),
                                ctypes.byref(tract_param_max), ctypes.byref(tract_param_neutral))
        self.__vt_names = tract_param_names.value.decode().split()
        vtp_max = list(tract_param_max)
        vtp_min = list(tract_param_min)
        vtp_def = list(tract_param_neutral)
        print('1')
        for i in range(len(self.__vt_names)):
            l = self.__vt_names[i]
            print(l)
            self.__mins[l] = vtp_min[i]
            self.__defs[l] = vtp_def[i]
            self.__maxs[l] = vtp_max[i]
            print(l)

        print('1')
        # Glottis parameters
        glottis_param_names = ctypes.c_char_p((' ' * 32 * gp_no).encode())
        glottis_param_min = GLOTTIS_PARAM_TYPE()
        glottis_param_max = GLOTTIS_PARAM_TYPE()
        glottis_param_neutral = GLOTTIS_PARAM_TYPE()
        # Extract glottis parameters information
        vt.vtlGetGlottisParamInfo(glottis_param_names, ctypes.byref(glottis_param_min),
                                  ctypes.byref(glottis_param_max), ctypes.byref(glottis_param_neutral))
        self.__g_names = glottis_param_names.value.decode().split()
        g_max = list(glottis_param_max)
        g_min = list(glottis_param_min)
        g_def = list(glottis_param_neutral)
        for i in range(len(self.__g_names)):
            l = self.__g_names[i]
            self.__mins[l] = g_min[i]
            self.__defs[l] = g_def[i]
            self.__maxs[l] = g_max[i]
        # Pressure adjustment:
        self.__defs['pressure'] = 0.0
        print('1')

    def getOrderedLabels(self, which=None):
        if which:
            if which == 'vocal': return self.__vt_names
            if which == 'glottis': return self.__g_names
        return self.__vt_names+self.__g_names

    # Labels used by the motor system
    def getMotorLabels(self):
        return self.__vt_names+['pressure', 'd_rest', 'f0']

    # TODO: change this
    def getDefaults(self):
        return self.__defs

    # TODO: change this
    def getMaxs(self):
        return self.__maxs

    # TODO: change this
    def getMins(self):
        return self.__mins

    def validate(self, key, new):
        if new < self.__mins[key]:
            return self.__mins[key]
        if new > self.__maxs[key]:
            return self.__maxs[key]
        return new

    def display(self):
        print('    Parameters as Label(min/def/max):')
        vt_info = list(k+'('+str(self.__mins[k])+'/'+str(self.__defs[k])+'/'+str(self.__maxs[k])+')  '
                       for k in self.__vt_names)
        g_info = list(k+'('+str(self.__mins[k])+'/'+str(self.__defs[k][1])+'/'+str(self.__maxs[k][2])+')  '
                      for k in ['pressure', 'f0', 'upper_rest_displacement', 'lower_rest_displacement'])
        print(' '.join(vt_info))
        print(' '.join(g_info))
