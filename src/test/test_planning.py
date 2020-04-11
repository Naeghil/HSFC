# -------------------------------------------------------------------------------
# Name:        test_planning
# Purpose:     Tests for critical methods for the syllable-level planning of motion.
#              The functions to be tested are: MotorPhonemePrograms._toLabels(),
#              MotorPhoenemePrograms._toSyllables()
#
# Author:      Roberto Sautto
#
# Last mod:    9/04/2020
# Copyright:   (c) Roberto Sautto 2020
# Licence:     <your licence>
# -------------------------------------------------------------------------------
# Global imports:
import random
import re
import string
import pytest
# Local imports
from ..model_components.syllable_level import MotorSyllablePrograms
from ..model_components._parameters_lists import ParList
from ..utils import RecoverableException

# The input to the tested functions is cascading: each function gives its output to the
# following one. Therefore I identify several equivalence classes for this kind of input:
# unacceptable strings: strings that contain unacceptable characters
# malformed strings: strings that don't produce acceptable syllables
# acceptable strings: strings that produce an acceptable plan in terms of targets
# Let
L = '['+string.ascii_lowercase+'_]'
# Let A = [aeioumbvndlzgh_] subset of L be the set of acceptable characters
# Let C subset of A:
C = '[mbdvnlz]'  # be the set of acceptable consonants (i.e. pretranslated consonants), except 'g'
# Let G:
G = '(gli|glia|gliu|ghi|ga|gu)'  # be the set of acceptable forms for g
# Let V subset of A:
V = '[aeiou]'  # be the set of acceptable vowels
# Let O subset of V:
O = '[aiu]'  # be the set of coarticulatable vowels,
# Let an acceptable word be:  ( (C*(O|G)) | V )V*
word = '(((('+C+'*('+O+'|'+G+'))|'+V+')'+V+'*)+)'
# unacceptable strings are of the form L*
# malformed strings are of the form:
malformed = '('+C+'|'+G+'|'+V+'|_)+\Z'
# acceptable strings are of the form:
acceptable = word+'(_'+word+')*\Z'

# The following are used for sample generation:
L_alphabet = L.replace('[', '').replace(']', '')
C_alphabet = C.replace('[', '').replace(']', '')
V_alphabet = V.replace('[', '').replace(']', '')
O_alphabet = O.replace('[', '').replace(']', '')
G_production = G.replace('(', '').replace(')', '').split('|')


def generate_word():
    to_produce = ''
    if random.random() > 0.5:
        for _ in range(random.randrange(1, 4)):
            to_produce += random.choice(list(V_alphabet))
        syllables = random.randrange(4)
    else:
        syllables = random.randrange(1, 5)
    for _ in range(syllables):
        syllable = ''
        for _ in range(random.randrange(1, 3)):
            consonant = random.choice(C_alphabet+'g')
            if consonant == 'g':
                syllable += random.choice(G_production)
                break
            syllable += consonant
        if list(syllable)[-1] not in list(O_alphabet):
            syllable += random.choice(O_alphabet)
        for _ in range(random.randrange(3)):
            syllable += random.choice(V_alphabet)
        to_produce += syllable
    return to_produce


def generate_cases():
    # Setup
    random.seed()
    unacceptable_list = []
    malformed_list = []
    isMalformed = re.compile(malformed).match
    acceptable_list = []
    isAcceptable = re.compile(acceptable).match

    # Generate unacceptable strings
    while len(unacceptable_list) < 20:
        current = ''.join(list(random.choice(L_alphabet) for _ in range(random.randrange(50))))
        if len(acceptable_list) < 20 and isAcceptable(current):
            acceptable_list.append(current)
        elif len(malformed_list) < 20 and isMalformed(current):
            malformed_list.append(current)
        else:
            unacceptable_list.append(current)
    # Generate malformed strings
    while len(malformed_list) < 20:
        current = ''.join(list(random.choice(list(C_alphabet)+G_production+list(V_alphabet))
                               for _ in range(random.randrange(1, 50))))
        if len(acceptable_list) < 20 and isAcceptable(current):
            acceptable_list.append(current)
        else:
            malformed_list.append(current)
    # Generate acceptable strings
    while len(acceptable_list) < 20:
        current = generate_word()
        for _ in range(random.randrange(4)):
            current += '_' + generate_word()
        if isAcceptable(current):
            acceptable_list.append(current)

    return unacceptable_list, malformed_list, acceptable_list


class MSPWrapper(MotorSyllablePrograms):
    def __init__(self):
        super(MSPWrapper, self).__init__({}, {}, {})

    # This function needs to be overridden, as it uses paramlists.Target
    # It would simply be harder to emulate the execution environment.
    # The correctness of the planned targets can easily be tested by
    # running the system.
    def _makeCommandList(self, words):
        return True

    # Make these functions public:
    def toSyllables(self, in_labels):
        return self._toSyllables(in_labels)

    def toLabels(self, in_list):
        # The following lines are from MotorSyllablePrograms.makePlan()
        if in_list == '':
            raise RecoverableException("I am already silent.")
        return self._toLabels(in_list)


def test_planning():
    # Simulating execution environment
    parameter_labels = []
    ParList.setIndexes(parameter_labels, parameter_labels)

    MSP = MSPWrapper()
    unacceptable_cases, malformed_cases, acceptable_cases = generate_cases()

    for case in unacceptable_cases:
        # The expected behaviour is the raising of a RecoverableException
        with pytest.raises(RecoverableException):
            print(case)
            MSP.toLabels(case)

    for case in malformed_cases:
        # The expected behaviour is the raising of specific RecoverableExceptions
        with pytest.raises(RecoverableException) as ex:
            print(case)
            labels = MSP.toLabels(case)
            MSP.toSyllables(labels)

        assert (("Unexpected end of word: a word can't end with a consonant" in str(ex.value)) or
                ("The first vowel of a non-starting syllable must be 'a', 'i' or 'u'" in str(ex.value)))

    for case in acceptable_cases:
        # The expected behaviour is termination of the execution
        print(case)
        labels = MSP.toLabels(case)
        MSP.toSyllables(labels)
