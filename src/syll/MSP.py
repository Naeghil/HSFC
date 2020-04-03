# -------------------------------------------------------------------------------
# Name:        Motor-Syllable Programs
# Purpose:     Module interpreting "conceptual" (input) signals into a motor plan
#
# Author:      Roberto Sautto
#
# Created:     04/03/2020
# Copyright:   (c) Roberto Sautto 2020
# Licence:     <your licence>
# -------------------------------------------------------------------------------
from src.utils.paramlists import Target


class MotorSyllablePrograms:
    # Built-in knowledge
    vowels = ['a', 'i', 'u']
    consonants = ['m', 'b', 'v', 'n', 'd', 'l', 'z', 'j\\', 'g']
    constant_times = {'l': 7.0, 'b': 15.0, 'd': 15.0, 'g': 15.0, 'm': 25.0, 'n': 25.0}

    def __init__(self, targets_reference):
        self.targets = targets_reference

    # This processes the input word to translate the "problematic" combinations of letters
    def __toLabels(self, in_list):
        ret = []
        i = 0
        max = len(in_list)-1
        while i <= max:
            if in_list[i] == 'g' and i < max:
                # Processes possibilities for "gli"->"j\\i", "ghi, ghe" -> "gi, ge"
                # The "gn" sound is not currently possible
                if i < max-1 and in_list[i+1] == 'l' and in_list[i+2] == 'i':
                    ret.append('j\\')
                    i += 1
                    if i < max-2 and in_list[i+3] in self.vowels:  # Assumes there is no 'glii'
                        i += 1
                elif i < max-1 and in_list[i+1] == 'h' and in_list[i+2] in ['i', 'e']:
                    ret.append('g')
                    i += 1
                else:
                    ret.append('g')
            elif in_list[i] == 'c':  # Not currently possible as there is no target for c
                # Processes possibilities for "ci, ce"->"ci, ce", "chi, che"->"ki, ke"
                pass
            elif i < max-1 and in_list[i] == 's' and in_list[i+1] == 'c' and in_list[i+2] in ['i', 'e']:
                # Not currently possible as there is no target for sh
                # Processes possibilities for "sci, sce" -> "shi, she"
                pass

            else:
                ret.append(in_list[i])
            i += 1

        return ret

    # TODO: this assumes only (CV)* words are produced; syllable division would be required otherwise
    def __makeCommandList(self, c_lab):
        f_lab = c_lab[0]
        if f_lab not in self.vowels:
            f_lab += c_lab[1]
        plan = [Target(5.0, self.targets[f_lab])]  # Vocalization target
        plan.insert(0, plan[0].makeNonPhonatory(10.0))  # Prevocalization target
        for i in range(1, len(c_lab)):
            if c_lab[i] in self.vowels:
                # The constant time (and thus effort) for a vowel target depends on the consonant preceding it
                plan.append(Target(self.constant_times.get(c_lab[i-1], 15.0), self.targets[c_lab[i]]))
            elif c_lab[i] == '_':
                plan.append(plan[-1].makeNonPhonatory(10.0))
                plan.append(Target(10.0, self.targets['_']))
            else:
                # Without further data from literature, the constant time for consonant targets is hand-tuned
                # This will most likely affect vowel length, but what is the cost for the articulated consonant?
                # TODO: at the moment words can only end with vowels; when they don't,
                #  the coarticulation target should be @
                plan.append(Target(15.0, self.targets[c_lab[i]+c_lab[i+1]]))

        plan.append(plan[-1].makeNonPhonatory(10.0))
        plan.append(Target(10.0, self.targets['_']))  # Relaxation
        return plan

    def makePlan(self, conc_input):
        in_labels = self.__toLabels(list(conc_input))
        return self.__makeCommandList(in_labels)
