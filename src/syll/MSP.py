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
    vowels = ['a', 'e', 'i', 'o', 'u']
    coart_vowels = ['a', 'i', 'u']
    consonants = ['m', 'b', 'v', 'n', 'd', 'l', 'z', 'j\\', 'g']
    constant_times = {'l': 7.0, 'b': 15.0, 'd': 15.0, 'g': 15.0, 'm': 25.0, 'n': 25.0}
    c_approach = 5.0  # Constant time for consonant approach
    vocalization = 10.0  # Constant time for vocalization
    devocalization = 10.0  # Constant time for devocalization
    # Following are the original constant times, as specified in
    # "Modeling Consonant-Vowel Coarticulation for Articulatory Speech Synthesis"
    # constant_times = {'l': 7.0, 'b': 15.0, 'd': 15.0, 'g': 15.0, 'm': 25.0, 'n': 25.0}

    def __init__(self, targets_reference):
        self.targets = targets_reference

    # This processes the input word to translate the "problematic" combinations of letters
    # NOTE: it's entirely possible to give the system an already "translated" string
    # NOTE: this does not deeply check for grammar and will allow for multiple vowels and consonants to
    # follow each other. If one wants to speak garbage, they're free to.
    def __toLabels(self, in_list):
        ret = []
        i = 0
        max = len(in_list)-1
        while i <= max:
            if in_list[i] in self.vowels:
                ret.append(in_list[i])
            elif in_list[i] in self.consonants:
                if in_list[i] == 'g':
                    # "gli" case:
                    if i < max-1 and in_list[i+1] == 'l' and in_list[i+2] == 'i':
                        ret.append('j\\')
                        i += 1
                        # glia/gliu case
                        if i < max-2 and in_list[i+3] in self.coart_vowels:
                            i += 1
                        else:
                            raise ValueError("Unexpected combination for 'gl'")
                    # ghi/ghe case
                    elif i < max-1 and in_list[i+1] == 'h':
                        if in_list[i+2] in ['i']:
                            ret.append('g')
                            i += 1
                        else:
                            raise ValueError('gh not followed by i')
                    # ga, gu and gC cases
                    else:
                        ret.append('g')
                # Not currently possible as there is no target for c
                elif in_list[i] == 'c':
                    pass
                # Not currently possible as there is no target for sh
                elif i < max-1 and in_list[i] == 's' and in_list[i+1] == 'c' and in_list[i+2] in ['i', 'e']:
                    pass
                else:
                    ret.append(in_list[i])
            else:
                raise ValueError("Unexpected consonant")
            i += 1
        return ret

    # A "syllable" is defined as a cycle of opening and closing of the vocal tract
    # In this function a syllable is a tuple: (targets_list, coarticulating_vowel)
    # The coarticulating vowel is the first vowel encountered
    def __toSyllables(self, in_labels):
        ret = []
        word = []
        syll = []
        i = 0
        while i < len(in_labels):
            curr = in_labels[i]
            # If '_' is encountered, the current word is ended
            if curr == '_':
                if i != 0 and not syll:
                    ret.append(word)
                    word = []
                else:
                    raise ValueError("Unexpected word-end character: a word can't end with a consonant")
            elif curr in self.consonants:
                syll.append(curr)
            elif curr in self.coart_vowels or (i == 0 and curr in self.vowels):
                syll.append(curr)
                while i+1 != len(in_labels) and in_labels[i+1] in self.vowels:
                    i += 1
                    syll.append(in_labels[i])
                word.append((syll, curr))
                syll = []
            else:
                raise ValueError("Unexpected target label: "+curr)
            i += 1
        if word:
            ret.append(word)
        if syll:
            # TODO: this can be avoided by coarticulating with @
            raise ValueError("A word cannot end with a consonant.")
        return ret

    # Converst syllables in a list of targets, which is ultimately the "motor" plan
    def __makeCommandList(self, words):
        ret = []
        for word in words:
            plan = []
            for syll in word:
                offset = 0
                # The first syllable in each word must reach the first target and then vocalize it
                if not plan:
                    first_lab = syll[0][0] + (syll[1] if syll[0][0] in self.consonants else '')
                    first = Target(5.0, self.targets[first_lab])  # Vocalization target
                    plan.append(first.makeNonPhonatory(self.vocalization))  # Prevocalization target
                    plan.append(first)
                    offset = 1
                for i in range(offset, len(syll[0])):
                    if syll[0][i] in self.vowels:
                        # The constant time (and thus effort) for a vowel target depends on the consonant preceding it
                        # If no consonant precedes it, this defaults to 15.0
                        ct = self.constant_times.get(syll[0][i-1], 15.0)
                        plan.append(Target(ct, self.targets[syll[0][i]]))
                    elif syll[0][i] in self.consonants:
                        coart_label = syll[0][i] + syll[1]
                        plan.append(Target(self.c_approach, self.targets[coart_label]))
                    else:
                        raise ValueError("Unexpected target label: " + syll[0][i])
            plan.append(plan[-1].makeNonPhonatory(self.devocalization))
            plan.append(Target(10.0, self.targets['_']))
            ret += plan

        return ret

    # Raises exceptions
    def makePlan(self, conc_input: list):
        if conc_input == '':
            raise ValueError("I am already silent.")
        in_labels = self.__toLabels(list(conc_input))
        syllables = self.__toSyllables(in_labels)
        return self.__makeCommandList(syllables)
