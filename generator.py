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
        self.rhymer = None
        self.ngramer = None


    def check_line_sonnet(new_stress, existing_stress):
        if len(new_stress) == 1 and len(existing_stress) == 9:
            return True # we allow the first syllable to be either stressed or unstressed if it's a single-syllable word
        return re.match(r'1?(01)*$', new_stress + existing_stress)


    def generate_line(self, currentRhyme, rhymes, syllable_len, check_line=None):
        words = [Ngramer.END_TOKEN]
        stress_line = ""
        attempts = 0

        while len(stress_line) < syllable_len and attempts < 20:
            attempts += 1
            # choose random words to begin
            if len(words) < 2: # picking end of line word
                if currentRhyme in rhymes:
                    word = self.rhymer.sample(rhymes[currentRhyme][-1])
                else:
                    word = self.ngramer.sample([...] + words[:1])
            else:
                word = self.ngramer.sample([...] + words[:1])

            if word is None or word == Ngramer.START_TOKEN:
                continue

            if len(words) < 2 and self.rhymer.rhyme_count(word) < 4:
                # Quick stop if we pick a first word that doesn't have very many rhymes
                continue

            stress = self.oov.stress_pattern(word)

            if len(stress + stress_line) > syllable_len:
                continue

            if check_line is None or check_line(stress, stress_line):
                stress_line = stress + stress_line
                words.insert(0, word)

        if len(stress_line) == syllable_len:
            return words[:-1]


    def generate(self, subreddit):
        self.ngramer = resources.ngramer(subreddit, SonnetGenerator.NGRAM_N)
        self.rhymer = resources.rhymer(subreddit)

        rhymeScheme = random.choice(SonnetGenerator.RHYME_SCHEMES)
        rhymes = defaultdict(list)
        sonnet = ""

        for linenum in range(len(rhymeScheme)):
            attempts = 0
            while attempts < 1000:
                attempts += 1

                currentRhyme = rhymeScheme[linenum]

                words = self.generate_line(currentRhyme, rhymes, 10, SonnetGenerator.check_line_sonnet)

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

    def generate_haiku(self, subreddit):
        self.ngramer = resources.ngramer(subreddit, SonnetGenerator.NGRAM_N)
        self.rhymer = resources.rhymer(subreddit)

        syl_scheme = [5, 7, 5]
        rhymes = defaultdict(list)
        haiku = ""

        for syl_count in syl_scheme:
            attempts = 0
            while attempts < 1000:
                attempts += 1

                words = self.generate_line('x', rhymes, syl_count)

                # save line
                if words is not None:
                    line = ' '.join((word.lower() for word in words))
                    cap = line[0].upper()
                    line = cap + line[1:]
                    haiku += line + '\n'
                    break
            if attempts == 1000:
                # Trouble generating? Insert [deleted]! (haha)
                haiku += '[deleted]\n'
        return haiku


if __name__ == "__main__":
    gen = SonnetGenerator()
    sonnet = gen.generate('environment')
    print(sonnet)