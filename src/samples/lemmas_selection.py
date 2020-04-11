# -------------------------------------------------------------------------------
# Name:        lemmas_selection
# Purpose:     Code used for the selection of sample candidates from
#              the CoLFIS corpus
#              # NOTE: this script must be run from HSFC/
#
# Author:      Naeghil
#
# Last mod:     07/04/2020
# Copyright:   (c) Naeghil 2020
# Licence:     <your licence>
# -------------------------------------------------------------------------------

# Global imports
import re

# Class of admitted characters
chlist = 'AEIOUMBVNDLZG'
# List of admitted consonants
conslist = 'MBVNDLZG'
# List of combinations of letters that are not synthesizable
unusedsyllables = r'(MO|ME|BO|BE|VO|VE|NO|NE|DO|DE|LO|LE|ZO|ZE|GLIO|GLIE|GO|GHE|GI|GE|GHI|GU|BI|BU|DU|GN)'
# List of combinations of letters that, while synthesizable, constitute syllables and thus cannot be word samples
notsamples = '\A(A|E|I|O|U|GA|BA|DA|DI|ZA|ZI|ZU|GLIA|GLI|GLIU|MA|MI|MU|NA|NI|NU|LA|LI|LU|VA|VI|VU)\Z'


def main():
    lemmas = open('resources/samples/Lemmas only.txt')
    lemmas = list(line.strip('\n') for line in lemmas)
    # Lemmas is now a list of records from the corpus

    tmp = lemmas
    lemmas = []
    for record in tmp:
        # Select only words of admitted characters
        if bool(re.match(r'\A([AEIOUMBVNDLZG])+\Z', record)):
            # Select only words ending with vowels
            if not (bool(re.search(r'[MBVNDLZG]\Z', record)) or
                    # Drops all words with syllables impossible to synthesize
                    bool(re.search(unusedsyllables, record)) or
                    # Drops all words that have a z that is not the start of the word
                    (bool(re.search(r'Z', record)) and not bool(re.search(r'\AZ', record))) or
                    bool(re.match(notsamples, record)) or  # Drops all words that would be syllables instead
                    bool(re.search(r'([AEIOUMBVNDLZG])\1', record))):  # Drops all words with double letters
                # Drops duplicates
                if record not in lemmas:
                    print(record)
                    lemmas.append(record)

    # Write the resulting candidates to file
    candidates = open('resources/samples/sample candidates.txt', 'w+')
    for lemma in lemmas:
        candidates.write(lemma.lower()+'\n')

    candidates.close()


if __name__ == '__main__':
    main()
