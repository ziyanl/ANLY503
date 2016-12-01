# can be imported and then called on alphanumeric strings with oov.guess_pron(word)
# or oov.guess_pron(word, CMUDICT=CMUDICT) for better performance

# NOTE: beginning of word often looks stupid because code ony cares about stress patterns
# and phonemes at the end of the word

import nltk, json
from collections import defaultdict, Counter
import pickle
import stress_perceptron

class Oov(object):
    def __init__(self):
        self.cache = {}
        self.cmudict = load_dict()

    def guess_pron(self, word):
        word = word.upper()
        if word not in self.cache:
            self.cache[word] = guess_pron(word, self.cmudict)
        return self.cache[word]

    def stress_pattern(self, word):
        pron = self.guess_pron(word)
        stress = ''
        for phoneme in pron:
            if phoneme[-1].isdigit():
                if phoneme[-1] == '0':
                    stress += '0'
                else:
                    stress += '1'
        return stress

def sonorance(letter):
    vowels = ['A', 'E', 'I', 'O', 'U', 'Y']
    approximants = ['L', 'R', 'W', 'Y', 'H']
    nasals = ['M', 'N']
    fricatives = ['F', 'J', 'V', 'Z']
    stops = ['B', 'D', 'G', 'K', 'P', 'T', 'C', 'Q', 'X']
    s = ['S']
    if letter in vowels:
        return 5
    if letter in approximants:
        return 4
    if letter in nasals:
        return 3
    if letter in fricatives:
        return 2
    if letter in stops:
        return 1
    if letter == 'S':
        return 0
    else:
        return 3  # ?


def ispronounceable(orth):
    '''
    :param orth: a token in orthographic form
    :return: False if spelling appears to violate phonotactic constraints and is likely to be an initialism; True otherwise
    '''
    if len(orth) < 2:
        return True

    # check beginning of word
    first = sonorance(orth[0])
    second = sonorance(orth[1])

    if first == 0:
        if second == 0 or second == 2:
            return False
    elif first == 1 or first == 2:
        if second < 4:
            return False
    elif first == 3 or first == 4:
        if second < 5:
            return False

    # check end of word
    if orth[-2] == orth[-1]:
        return True
    elif orth[-2:] in ['TH', 'CH', 'SH']:
        return True
    else:
        penult = sonorance(orth[-2])
        last = sonorance(orth[-1])

        # if last == 0 or last == 1:
        #     if penult == 2:
        #         return False
        if last == 2:
            if penult < 4:
                return False
        elif last == 3:
            if 0 < penult < 4:
                return False
        elif last == 4:
            if penult < 5:
                if orth[:2] != 'WH':
                    return False

    return True


def isvoiceless(phoneme):
    return phoneme in ['F', 'K', 'P', 'T', 'TH', 'S', 'SH', 'CH']


def end_match(word1, word2):
    '''
    :param word1, word2: two orthographic words
    :return: int representing how many letters match at the end of the word
    '''
    i = 1
    while i <= len(word1) and i <= len(word2):
        if word1[-i:] != word2[-i:]:
            return i - 1
        else:
            i += 1
    return i - 1


def end_pron(prons):
    '''
    :param prons: list of pronunciations (each a list of phonemes)
    :return: partial pron (list of phonemes) representing the most common ending
    '''
    if len(prons) == 0:
        return []
    elif len(prons) == 1:
        nostress = []
        for phon in prons[0]:
            if phon[-1].isdigit():
                nostress.append(phon[:-1])
            else:
                nostress.append(phon)

        return nostress
    else:
        lasts = defaultdict(list)
        lastcounts = Counter()
        for pron in prons:
            last = pron[-1]
            if last[-1].isdigit():
                last = last[:-1]
            lasts[last].append(pron)
            lastcounts[last] += 1
        # print(lastcounts.most_common(1))
        best = lastcounts.most_common(1)
        best_phon = best[0][0]
        new_prons = []
        for pron in lasts[best_phon]:
            if len(pron) > 1:
                new_prons.append(pron[:-1])
        else:
            recurse = end_pron(new_prons)
            recurse.append(best_phon)
            return recurse


def numberpron(numeric, CMUDICT):
    dig_map = {'1': 'ONE', '2': 'TWO', '3': 'THREE', '4': 'FOUR', '5': 'FIVE', '6': 'SIX', '7': 'SEVEN', '8': 'EIGHT',
               '9': 'NINE', '0': 'ZERO'}
    tens_map = {'2': 'TWENTY', '3': 'THIRTY', '4': 'FORTY', '5': 'FIFTY', '6': 'SIXTY', '7': 'SEVENTY', '8': 'EIGHTY',
                '9': 'NINETY', '0': 'OH'}
    teens_map = {'10': 'TEN', '11': 'ELEVEN', '12': 'TWELVE', '13': 'THIRTEEN', '14': 'FOURTEEN', '15': 'FIFTEEN',
                 '16': 'SIXTEEN', '17': 'SEVENTEEN', '18': 'EIGHTEEN', '19': 'NINETEEN'}

    if len(numeric) == 1:
        try:
            return CMUDICT[dig_map[numeric]]
        except:
            return []

    if len(numeric) == 2:
        if numeric[0] == '1':
            return CMUDICT[teens_map[numeric]]
        elif numeric[1] == '0':
            return CMUDICT[tens_map[numeric[0]]]
        else:
            return CMUDICT[tens_map[numeric[0]]] + CMUDICT[dig_map[numeric[1]]]

    if len(numeric) == 3:
        return numberpron(numeric[0], CMUDICT) + numberpron(numeric[1:3], CMUDICT)

    if len(numeric) == 4:
        return numberpron(numeric[0:2], CMUDICT) + numberpron(numeric[2:4], CMUDICT)

    pron = []
    for digit in numeric:
        dig_pron = CMUDICT[dig_map[digit]]
        pron += dig_pron
    return pron


def load_dict():
    """Load cmudict.json into the CMUDICT dict."""
    CMUDICT = {}
    INPUT_PATH = 'data/pronunciations.json'
    with open(INPUT_PATH) as json_file:
            CMUDICT = json.load(json_file)
    return CMUDICT


def guess_pron(word, CMUDICT):
    '''
    :param word: alphanumeric string
    :param CMUDICT: CMU pronouncing dictionary loaded into a dictionary
    :return: guess at the pronunciation of the word, in CMUDICT format; focuses on ending phonemes and
    syllable count/stress patterns, so phonemes near the beginning of the word may be very weird
    '''

    # first check if word is in CMUDICT, if so, just return that results
    if word in CMUDICT:
        return CMUDICT[word]

    # numbers
    if word.isnumeric():
        return numberpron(word, CMUDICT)

    # try singular
    if word[-1] == 'S':  # TODO: deal better with more complex plurals, orthographically and phonologically, e.g. sibilants, -ies
        sg = word[:-1]
        if sg in CMUDICT:
            sgpron = CMUDICT[sg]
            plpron = []
            if isvoiceless(sgpron[-1]):
                plpron = sgpron + ['S']
            else:
                plpron = sgpron + ['Z']
            return plpron

    # phonotactically bad things are treated as acronyms (probably never iamb-compatible)
    if ispronounceable(word) is False:
        pron = []
        for char in word:
            try:
                pron += CMUDICT[char]
            except:
                pron += guess_pron(char, CMUDICT=CMUDICT)
        return pron

    # try string-matching end of word
    # pass over cmudict, keep track of length of greatest match and words with that match
    max_match = 0
    matches = []
    for key in CMUDICT.keys():
        match_len = end_match(word, key)
        if match_len > max_match:
            max_match = match_len
            matches = [key]
        elif match_len == max_match:
            matches.append(key)

    # for things with weird characters; hacky way to return something ineligible for sonnet use
    if max_match == 0:
        return ['UU1', 'UU1']

    match_prons = []
    for match in matches:
        match_prons.append(CMUDICT[match])

    end = end_pron(match_prons)
    #print(word, matches, end)

    # use perceptron (pre-learned weights/biases and scoring method) to guess stress pattern
    p = stress_perceptron.Perceptron(weights='weights_5.pk', biases='biases_5.pk')
    features = stress_perceptron.extract_feats(word)
    stress = p.predict(features)
    #print(word, end, stress)

    # ???? hacky way to deal with words with more than 5 syllables; should just eliminate them from being used in a sonnet
    if stress == 'too_long':
        stress = '111111'

    # integrate end phonemes with stress
    guess = []
    for phon in end[::-1]:
        if phon[0] in ['A', 'E', 'I', 'O', 'U']:
            if len(stress) == 0:
                return guess
            else:
                stressed = phon + stress[-1]
                guess = [stressed] + guess
                stress = stress[:-1]
        else:
            guess = [phon] + guess

    if len(stress) > 0:
        for num in stress[::-1]:
            phon = 'UU' + str(num)  # fake vowel
            guess = [phon] + guess

    return guess


if __name__ == "__main__":
    '''for testing'''
    CMUDICT = load_dict()
    OOV = defaultdict(int)

    with open("philosophy-comments.txt") as infile:
        filestring = infile.read()
        tokens = nltk.word_tokenize(filestring)

        for tok in tokens:
            tok = tok.upper()
            if tok not in CMUDICT:
                OOV[tok] += 1

    OOV = sorted(OOV, key=OOV.get, reverse=True)

    for tok in OOV:
        if tok.isalnum():
            print(tok, str(guess_pron(tok, CMUDICT=CMUDICT)))
