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
from rhymer import Rhymer
from text_cleaner import TextCleaner

# import pandas

repeat = re.compile("[A-Z']*\\([0-9]+\\)")
whitespace = re.compile("\\s+")


# function for removing whitespace in lines
def split_line(line):
    syllables = filter(None, whitespace.split(line))
    return ' '.join(syllables)


def get_stress_pattern(pattern):
    nums = []
    for count in pattern:
        if count.isdigit():
            nums.append(1 if int(count) > 0 else 0)
    return nums


def load_ngrams_and_rhymes(subreddit, oovObj, n=2):
    """
    Loads and returns an Ngramer and Rhymer instance for the given subreddit.
    Will cache results to disk for faster loading on subsequent requests.
    """
    ngramer = None
    ngram_path = util.path_to_data_directory() + "{}.{}gram".format(subreddit, n)
    if os.path.exists(ngram_path):
        # Load the cached ngram model
        with open(ngram_path, 'r') as f:
            ngramer = Ngramer.read(f, n)

    rhymer = None
    rhymer_path = util.path_to_data_directory() + '{}.rhymes'.format(subreddit)
    if os.path.exists(rhymer_path):
        # Load the cached ngram model
        with open(rhymer_path, 'r') as f:
            rhymer = Rhymer.read(f, oovObj)

    if ngramer is None or rhymer is None:
        # Generate the ngram model from the raw text document
        tc = TextCleaner()
        try:
            with open(util.path_to_data_directory() + "{}-comments.txt".format(subreddit)) as f:
                print('cleaning')
                clean_lines = [tc.clean_text(line).text for line in f]
                if ngramer is None: # cache for future use
                    print('generating ngrams')
                    ngramer = Ngramer.from_text(clean_lines, n)
                    with open(ngram_path, 'w') as f:
                        ngramer.write(f)
                if rhymer is None: # cache for future use
                    print('generating rhymes')
                    rhymer = Rhymer.from_text(clean_lines, oovObj)
                    with open(rhymer_path, 'w') as f:
                        rhymer.write(f)
        except FileNotFoundError:
            raise ValueError('{} not loaded, try another or run subreddit_scrape'.format(subreddit))

    return ngramer, rhymer


def check_line(stress_line):
    # if stress_line == '1101010101':
    #     return True
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

def generate_line(currentRhyme, rhymes, rhymer, ngramer, oovObj):
    words = [Ngramer.END_TOKEN]
    stress_line = ""
    attempts = 0

    while len(stress_line) < 10 and attempts < 20:
        attempts += 1
        # choose random words to begin
        if len(words) < 2: # picking end of line word
            if currentRhyme in rhymes:
                word = rhymer.sample(rhymes[currentRhyme][-1])
            else:
                word = ngramer.sample([...] + words[:1])
        else:
            word = ngramer.sample([...] + words[:1])

        if word is None:
            continue

        if len(words) < 2 and rhymer.rhyme_count(word) < 4:
            # Quick stop if we pick a first word that doesn't have very many rhymes
            continue

        stress = oovObj.stress_pattern(word)

        if check_line(stress + stress_line) or (len(stress) == 1 and len(stress_line) == 9):
            stress_line = stress + stress_line
            words.insert(0, word)

    if len(stress_line) == 10:
        return words[:-1]


def generate(subreddit):
    oovObj = oov.Oov()

    # TODO: We need the text cleaner to scrub the reddit data first

    ngramer, rhymer = load_ngrams_and_rhymes(subreddit, oovObj)

    rhymeSchemes = [
        # source: http://www.rc.umd.edu/sites/default/RCOldSite/www/rchs/sonnet.htm
        "ABBAABBACDECDE", # standard Petrarchan
        "ABBAABBACDCDCD", # Petrarchan variant
        "ABBAABBACDEDCE",  # Petrarchan variant
        "ABBAACCACDECDE", # Wordsworth's Petrarchan variant
        "ABABCDCDEFEFGG", # standard Shakespearean
        "ABABBCBCCDCDEE" # Spenserian
    ]
    rhymeScheme = random.choice(rhymeSchemes)
    rhymes = defaultdict(list)
    sonnet = ""

    for linenum in range(len(rhymeScheme)):
        attempts = 0
        while attempts < 1000:
            attempts += 1

            currentRhyme = rhymeScheme[linenum]

            words = generate_line(currentRhyme, rhymes, rhymer, ngramer, oovObj)

            # save line
            if words is not None:
                rhymes[currentRhyme].append(words[-1])
                line = ' '.join((word.lower() for word in words))
                cap = line[0].upper()
                line = cap + line[1:]
                if linenum == 13:
                    line += '.'
                else:
                    line += ','
                sonnet += line + '\n'
                break
        if attempts == 1000:
            # Trouble generating? Insert [deleted]! (haha)
            sonnet += '[deleted]\n'
    return sonnet

if __name__ == "__main__":
    print(generate('washingtondc'))
