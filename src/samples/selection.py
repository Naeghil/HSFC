# -------------------------------------------------------------------------------
# Name:        selection
# Purpose:     Code used for the selection of sample candidates from
#              the CoLFIS corpus
#
# Author:      Naeghil
#
# Last mod:     07/04/2020
# Copyright:   (c) Naeghil 2020
# Licence:     <your licence>
# -------------------------------------------------------------------------------

# List of admitted characters
chlist = ['A', 'E', 'I', 'O', 'U', 'M', 'B', 'V', 'N', 'D', 'L', 'Z', 'G']
# List of admitted consonants
conslist = ['M', 'B', 'V', 'N', 'D', 'L', 'Z', 'G']
# List of combinations of letters that are not synthesizable
unusedsyllables = ['MO', 'ME', 'BO', 'BE', 'VO', 'VE', 'NO', 'NE', 'DO', 'DE', 'LO', 'LE', 'ZO', 'ZE', 'GLIO', 'GLIE',
                   'GO', 'GHE', 'GI', 'GE', 'GHI', 'GU', 'BI', 'BU', 'DU', 'GN']
# List of combinations of letters that, while synthesizable, constitute syllables and thus cannot be word samples
notsamples = ['A', 'E', 'I', 'O', 'U', 'GA', 'BA', 'DA', 'DI', 'ZA', 'ZI', 'ZU', 'GLIA', 'GLI', 'GLIU', 'MA', 'MI',
              'MU', 'NA', 'NI', 'NU', 'LA', 'LI', 'LU', 'VA', 'VI', 'VU']


def main():
    lemmas = open('../../resources/Lemmas only.txt')
    lemmas = list(line for line in lemmas)
    lemmas = list(line.strip('\n') for line in lemmas)
    # Lemmas is now a list of records from the corpus

    # Select only words of admitted characters
    tmp = lemmas
    lemmas = []
    for record in tmp:
        toinc = True
        for character in list(record):
            if character not in chlist:
                toinc = False
                break
        if toinc:
            lemmas.append(record)

    # Select only words ending with vowels
    tmp = lemmas
    lemmas = []
    for record in tmp:
        if record == '':
            continue
        if list(record)[-1] not in conslist:
            lemmas.append(record)

    # Drops all words with syllables impossible to synthesize
    tmp = lemmas
    lemmas = []
    for record in tmp:
        toinc = True
        for syll in unusedsyllables:
            if syll in record:
                toinc = False
                break
        if toinc:
            lemmas.append(record)

    # Drops all duplicates
    tmp = lemmas
    lemmas = []
    for record in tmp:
        if record not in lemmas:
            lemmas.append(record)

    # Drops all words that would be syllables instead
    tmp = lemmas
    lemmas = []
    for record in tmp:
        if record not in notsamples:
            lemmas.append(record)

    # Drops all words with double letters
    tmp = lemmas
    lemmas = []
    for record in tmp:
        rec = list(record)
        toinc = True
        for i in range(1, len(rec)):
            if rec[i] == rec[i - 1]:
                toinc = False
                break
        if toinc:
            lemmas.append(record)

    # Write the resulting candidates to file
    candidates = open('../../resources/sample candidates.txt', 'w+')
    for lemma in lemmas:
        candidates.write(lemma.lower()+'\n')

    candidates.close()


if __name__ == '__main__':
    main()
