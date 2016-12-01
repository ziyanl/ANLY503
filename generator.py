# -*- coding: utf-8 -*-
# !/usr/bin/python

import os
import re
import random
import oov
from collections import defaultdict
from ngramer import Ngramer
import resources


class SonnetGenerator(object):


    NGRAM_N = 2


    RHYME_SCHEMES = [
        # source: http://www.rc.umd.edu/sites/default/RCOldSite/www/rchs/sonnet.htm
        "ABBAABBACDECDE", # standard Petrarchan
        "ABBAABBACDCDCD", # Petrarchan variant
        "ABBAABBACDEDCE",  # Petrarchan variant
        "ABBAACCACDECDE", # Wordsworth's Petrarchan variant
        "ABABCDCDEFEFGG", # standard Shakespearean
        "ABABBCBCCDCDEE" # Spenserian
    ]


    def __init__(self):
        self.oov = oov.Oov()


    def check_line(self, stress_line):
        # if stress_line == '1101010101':
        #     return True
        return len(stress_line) <= 10 and re.match(r'1?(01)*$', stress_line)


    def generate_line(self, currentRhyme, rhymes, rhymer, ngramer):
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

            stress = self.oov.stress_pattern(word)

            if self.check_line(stress + stress_line) or (len(stress) == 1 and len(stress_line) == 9):
                stress_line = stress + stress_line
                words.insert(0, word)

        if len(stress_line) == 10:
            return words[:-1]


    def generate(self, subreddit):
        ngramer = resources.ngramer(subreddit, SonnetGenerator.NGRAM_N)
        rhymer = resources.rhymer(subreddit)

        rhymeScheme = random.choice(SonnetGenerator.RHYME_SCHEMES)
        rhymes = defaultdict(list)
        sonnet = ""

        for linenum in range(len(rhymeScheme)):
            attempts = 0
            while attempts < 1000:
                attempts += 1

                currentRhyme = rhymeScheme[linenum]

                words = self.generate_line(currentRhyme, rhymes, rhymer, ngramer)

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
    gen = SonnetGenerator()
    sonnet = gen.generate('starwars')
    print(sonnet)