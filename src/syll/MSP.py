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
    consonants = ['m', 'b', 'v', 'n', 'd', 'N', 'l', 's', 'z', 'j\\', 'g']
    constant_times = {'l': 7.0, 'b': 15.0, 'd': 15.0, 'g': 15.0, 'm': 25.0, 'n': 25.0}

    def __init__(self, targets_reference):
        self.targets = targets_reference

    # This processes the input word to translate the "problematic" combinations of letters
    def __toLabels(self, in_list):
        ret = []
        i = 0
        max = len(in_list)-1
        while i <= max:
            print(in_list[i])
            if in_list[i] == 'g' and i < max:
                # Processes possibilities for "gn"->N, "gli"->"j\\i", "gi, ge"->"zi, ze", "ghi, ghe" -> "gi, ge"
                if in_list[i+1] == 'n':
                    ret.append('N')
                    i += 1
                elif i < max-1 and in_list[i+1] == 'l' and in_list[i+2] == 'i':
                    ret.append('j\\')
                    i += 1
                elif in_list[i+1] in ['i', 'e']:
                    ret.append('z')
                elif in_list[i+1] == 'h':
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
            print(ret)

        return ret

    def __makeCommandList(self, labels_list):
        plan = [Target(labels_list[0], 5.0)]  # Vocalization target
        plan.insert(0, plan[0].makeNonPhonatory(10.0))  # Prevocalization target
        # TODO: this assumes only (CV)* words are produced; syllable division would be required otherwise
        for i in range(1, len(labels_list)):
            if labels_list[i] in self.vowels:
                # The constant time (and thus effort) for a vowel target depends on the consonant preceding it
                plan.append(Target(self.constant_times.get(labels_list[i-1], 15.0), self.targets[i]))
            else:
                # Without further data from literature, the constant time for consonant targets is hand-tuned
                # This will most likely affect vowel length, but what is the cost for the articulated consonant?
                plan.append(Target(15.0, self.targets[i]))

        plan.append(plan[-1].makeNonPhonatory(5.0))
        plan.append(Target(10.0, self.targets['_']))  # Relaxation
        return plan

    def makePlan(self, conc_input):
        in_labels = self.__toLabels(list(conc_input))
        print(in_labels)

