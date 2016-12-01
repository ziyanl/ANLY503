# -*- coding: utf-8 -*-
# !/usr/bin/python

import os
import re
import sys
import random
import sqlite3
import oov
import json
from collections import defaultdict
import scraping.pronunciations as pron
import utilities as util
from ngramer import Ngramer
from text_cleaner import TextCleaner

# import pandas

repeat = re.compile("[A-Z']*\\([0-9]+\\)")
whitespace = re.compile("\\s+")


# function for removing whitespace in lines
def split_line(line):
    syllables = filter(None, whitespace.split(line))
    return ' '.join(syllables)


def load_dict():
    """Load cmudict.json into the CMUDICT dict."""
    CMUDICT = {}
    INPUT_PATH = 'data/pronunciations.json'
    with open(INPUT_PATH) as json_file:
            CMUDICT = json.load(json_file)
    return CMUDICT


def get_stress_pattern(pattern):
    nums = []
    for count in pattern:
        if count.isdigit():
            nums.append(1 if int(count) > 0 else 0)
    return nums


def load_ngrams(subreddit, n=2):
    """
    Loads and returns an Ngramer instance for the given subreddit.
    Will cache results to disk for faster loading on subsequent requests.
    """
    ngram_path = util.path_to_data_directory() + "{}.{}gram".format(subreddit, n)
    if os.path.exists(ngram_path):
        # Load the cached ngram model
        with open(ngram_path, 'r') as f:
            return Ngramer.read(f, n)
    else:
        # Generate the ngram model from the raw text document
        tc = TextCleaner()
        try:
            with open(util.path_to_data_directory() + "{}-comments.txt".format(subreddit)) as f:
                ngramer = Ngramer.from_text((tc.clean_text(line).text for line in f), n)
        except FileNotFoundError:
            raise ValueError('{} not loaded, try another or run subreddit_scrape'.format(subreddit))
        # Cache the ngram model to disc for next time
        with open(ngram_path, 'w') as f:
            ngramer.write(f)
        return ngramer


def check_line(stress_line):
    if stress_line == '1101010101':
        return True
    return len(stress_line) <= 10 and re.match(r'1?(01)*$', stress_line)

def get_rhyme(pron):
    '''
    :param pron: pronunciation of a word
    :return: list of phonemes representing the end of the word starting with the last stressed vowel
    '''
    rhyme = []
    for phon in pron[::-1]:
        rhyme.insert(0, phon)
        if phon[-1] == '1':
            return rhyme
    return rhyme

if __name__ == "__main__":
    CMUDICT = load_dict()

    # TODO: We need the text cleaner to scrub the reddit data first

    #create_db()
    ngramer = load_ngrams("starwars")

    #connection = sqlite3.connect('starwars-comments.db')
    #cur = connection.cursor()

    rhymeScheme = "ABABCDCDEFEFGG"
    rhymes = defaultdict(list)

    for linenum in range(len(rhymeScheme)):
        words = ['</s>']
        stress_line = ""
        lastSyllableStressed = True
        numSyllables = 0
        currentRhyme = rhymeScheme[linenum]

        while len(stress_line) < 10:

            # choose random words to begin
            if len(words) < 2: # picking end of line word
                if currentRhyme in rhymes:
                    word = None
                    for i in range(2000):
                        tmp_word = ngramer.sample_unigram()
                        if get_rhyme(tmp_word) == get_rhyme(rhymes[currentRhyme][0]) and tmp_word not in rhymes[currentRhyme]:
                            word = tmp_word
                            break
                    if word is None:
                        word = random.choice(rhymes[currentRhyme])
                else:
                    word = ngramer.sample([...] + words[-1:])
            else:
                word = ngramer.sample([...] + words[-1:])
            #print(word)

            pron = oov.guess_pron(word.upper(), CMUDICT=CMUDICT)
            stress = ''
            for phoneme in pron:
                if phoneme[-1].isdigit():
                    if phoneme[-1] == '0':
                        stress += '0'
                    else:
                        stress += '1'

            if check_line(stress + stress_line):
                stress_line = stress + stress_line
                words.insert(0, word)
                #print(words)

        # print line
        rhymes[currentRhyme].append(words[-2])
        print(' '.join(words[:-1]))
