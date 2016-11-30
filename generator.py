# -*- coding: utf-8 -*-
# !/usr/bin/python

import re
import sys
import random
import sqlite3
import oov
import json
import scraping.pronunciations as pron

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
    INPUT_PATH = 'cmudict.json'
    with open(INPUT_PATH) as json_file:
        for line in json_file:
            obj = json.loads(line)
            word = obj["word"]
            prons = obj["pronunciations"]
            CMUDICT[word] = prons
    return CMUDICT


def select_words():
    CMUDICT = pron.clean_pronunciations()
    return [word for word in CMUDICT]


# function for stress pattern verification
def stress_pattern(stressed, s):
    nums = [1 if stressed else 0]
    for count in s:
        nums.append(int(count))
    bad = False
    for i in range(len(nums) - 1):
        if nums[i] == nums[i + 1]:
            bad = True
            break
    return not bad


def get_stress_pattern(pattern):
    nums = []
    for count in pattern:
        if count.isdigit():
            nums.append(1 if int(count) > 0 else 0)
    return nums


def create_db():
    # create starwars-comments database
    connection = sqlite3.connect('starwars-comments.db')
    cur = connection.cursor()

    # create table
    cur.execute('''CREATE TABLE starwars-comments (TEXT)''')

    # read starwars-comments text file
    file = open("starwars-comments.txt", "r")
    starwars = file.read()

    # write text data into database
    for row in starwars:
        cur.execute('INSERT INTO starwars-comments VALUES(TEXT)', row)

    # save changes
    connection.commit()

    # close tect file    
    file.close()
    # close connection
    # conn.close()


if __name__ == "__main__":
    words = select_words()

    # TODO: We need the text cleaner to scrub the reddit data first

    create_db()

    connection = sqlite3.connect('starwars-comments.db')
    cur = connection.cursor()

    rhymeScheme = "ABABCDCDEFEFGG"
    rhymes = dict()

    for linenum in range(len(rhymeScheme)):
        line = ""
        lastSyllableStressed = True
        numSyllables = 0
        currentRhyme = rhymeScheme[linenum]

        while numSyllables < 10:
            # choose random words to begin
            word = random.choice(words)
            # find all matching words
            matching = cur.execute("SELECT * FROM words WHERE word = ?", (word,)).fetchall()

            # add syllables to lines
            # stressed = 1, unstressed = 0
            for match in matching:
                _, rhym, syls, strs, cmmn = match

                # skip if already has more than 10 syllables
                if syls + numSyllables > 10:
                    continue

                # verify stress patterns
                if not stress_pattern(lastSyllableStressed, strs):
                    continue

                # fit rhymes of the last word
                if syls + numSyllables == 10:

                    try:
                        if rhym != rhymes[currentRhyme]:
                            continue
                    except KeyError:
                        rhymes[currentRhyme] = rhym

                line += word + " "
                lastSyllableStressed = strs[-1] == '1'
                numSyllables += syls
                break

        # print line              
        print(line)
