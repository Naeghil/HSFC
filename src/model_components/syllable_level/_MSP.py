# -------------------------------------------------------------------------------
# Name:        MSP
# Purpose:     Originally meant as a subcomponent of HSFC, it provides similar
#              functionalities, by translating a "conceptual signal" (user input)
#              in a plan understandable by the system. It's responsible for
#              planning at a "syllable" level (see Report)
#
# Author:      Roberto Sautto
#
# Last mod:     07/04/2020
# Copyright:   (c) Roberto Sautto 2020
# Licence:     <your licence>
# -------------------------------------------------------------------------------

# Local imports
from .._parameters_lists import Target
from ...utils import RecoverableException, UnrecoverableException


class MotorSyllablePrograms:
    # HARDCODED
    vowels = ['a', 'e', 'i', 'o', 'u']  # All vowels the system is able to produce
    coart_vowels = ['a', 'i', 'u']  # All vowels that can currently be coarticulated
    consonants = ['m', 'b', 'v', 'n', 'd', 'l', 'z', 'j\\', 'g']  # All consonants the system is able to produce
    vocalization = 15.0  # Constant time for vocalization

    # These are references to SPT's data
    def __init__(self, targets_reference: dict, vow_ct_reference: dict, con_ct_reference: dict):
        self.targets = targets_reference
        self.vow_approach = vow_ct_reference
        self.con_approach = con_ct_reference

    # This processes the input word to translate the "problematic" combinations of letters
    # NOTE: it's entirely possible to give the system an already "translated" string
    # NOTE: this does not deeply check for grammar and will allow for multiple vowels and consonants to
    # follow each other. If one wants to speak garbage, they're free to.
    def _toLabels(self, in_list):
        ret = []
        i = 0
        max = len(in_list)-1
        while i <= max:
            # HARDCODED
            if in_list[i] in self.vowels:
                ret.append(in_list[i])
            elif in_list[i] in self.consonants+['_']:
                if in_list[i] == 'g' and i < max:
                    # "gli" case:
                    if i < max-1 and in_list[i+1] == 'l':
                        if in_list[i+2] == 'i':
                            ret.append('j\\')
                            i += 1
                        else:
                            raise RecoverableException("Unexpected combination for 'gl'"+in_list[i+2])
                    # ghi/ghe case
                    elif i < max-1 and in_list[i+1] == 'h':
                        if in_list[i+2] in ['i']:
                            ret.append('g')
                            i += 1
                        else:
                            raise RecoverableException('gh not followed by i')
                    # gi/ge/gn not synthesizable
                    elif in_list[i+1] in self.consonants+['a', 'u'] and in_list[i+1] != 'n':
                        ret.append('g')
                    else:
                        raise RecoverableException("Combination not allowed: g"+in_list[i+1])
                else:
                    ret.append(in_list[i])
            else:
                raise RecoverableException("Unexpected character")
            i += 1
        return ret

    # A "syllable" is defined as a cycle of opening and closing of the vocal tract
    # In this function a syllable is a tuple: (targets_list, coarticulating_vowel)
    # The coarticulating vowel is the first vowel encountered
    def _toSyllables(self, in_labels):
        ret, word, syll = [], [], []
        i = 0
        while i < len(in_labels):
            # Append all consonants, if any
            while i < len(in_labels) and in_labels[i] in self.consonants:
                syll.append(in_labels[i])
                i += 1
            # Append all vowels (the first condition eliminates the in_labels[i]=='_' possibility
            if (not word and not syll and in_labels[i] in self.vowels) or \
                    (i < len(in_labels) and in_labels[i] in self.coart_vowels):
                syll.append(in_labels[i])
                coart = in_labels[i]
                i += 1
                # Append all other vowels, if any
                while i < len(in_labels) and in_labels[i] in self.vowels:
                    syll.append(in_labels[i])
                    i += 1
                # At this point, the syllable is over
                word.append((syll, coart))
                syll = []
            # Wrong first vowel
            elif i != 0 and i < len(in_labels) and in_labels[i] != '_':
                print(syll)
                print(word)
                print(in_labels[i])
                raise RecoverableException("The first vowel of a non-starting syllable must be 'a', 'i' or 'u'")

            # Word is signaled over
            if i >= len(in_labels) or in_labels[i] == '_':
                # If the syllable wasn't over, the word ending is wrong
                if syll:
                    raise RecoverableException("Unexpected end of word: a word can't end with a consonant")
                else:
                    ret.append(word)
                    word = []
                    i += 1
        return ret

    # Converst syllables in a list of targets, which is ultimately the "motor" plan
    def _makeCommandList(self, words):
        ret = []
        for word in words:
            plan = []
            for syll in word:
                offset = 0
                # The first syllable in each word must reach the first target and then vocalize it
                if not plan:
                    # Label of the first target: either a vowel or a coarticulated consonant
                    first_lab = syll[0][0] + (syll[1] if syll[0][0] in self.consonants else '')
                    # raises UnrecoverableException
                    first = Target(self.con_approach.get(syll[0][0], 10.0),
                                   self.targets.get(first_lab, []))  # First target, vocalized
                    plan.append(first.makeNonPhonatory(10.0))  # Prevocalization target
                    plan.append(first)  # Vocalization target
                    offset = 1
                # Subsequent syllables are more straightforward
                for i in range(offset, len(syll[0])):
                    if syll[0][i] in self.vowels:
                        # The constant time for a vowel target depends on the consonant preceding it
                        ct = self.vow_approach.get(syll[0][i-1], 10.0)  # Defaults to 10.0
                        plan.append(Target(ct, self.targets.get(syll[0][i], [])))  # raises UnrecoverableException
                    elif syll[0][i] in self.consonants:
                        coart_label = syll[0][i] + syll[1]  # The label of the coarticulated consonant
                        ct = self.con_approach.get(syll[0][i], 15.0)  # The constant time for the consonant
                        plan.append(Target(ct, self.targets.get(coart_label, [])))  # raises UnrecoverableException
                    else:
                        raise UnrecoverableException("Unexpected target label: " + syll[0][i] + ". This is a bug.")
            # After the utterance is over, pressure goes to 0 and the vocal tract "relaxes"
            plan.append(plan[-1].makeNonPhonatory(10.0))
            plan.append(Target(10.0, self.targets.get('_', [])))
            ret += plan

        return ret

    # Plans the speech for the user input
    def makePlan(self, conc_input: list):
        if conc_input == '':
            raise RecoverableException("I am already silent.")
        # Converts to labels
        in_labels = self._toLabels(list(conc_input))  # raises RecoverableException
        # Divides in syllables
        syllables = self._toSyllables(in_labels)  # raises RecoverableException
        # Constructs articulatory targets
        return self._makeCommandList(syllables)  # raises UnrecoverableException
