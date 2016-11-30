# -*- coding: utf-8 -*-
#!/usr/bin/python

import re
import sys
import random
import sqlite3
import oov
import json

global words
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
    global words
    words = []
    CMUDICT = load_dict()
    
    with open('cmudict_0.7b.txt','r') as file:
        for line in file:
            line = split_line(line)
            # skip comments and line not beginning with letter
            if not line[0].isalpha():
                continue

            syllables = line.split(' ', 1)
            word = syllables[0]
            
            oov.guess_pron(word, CMUDICT=CMUDICT)
            
            if repeat.match(word):
                continue
            # add word to words[] if not there
            words.append(word)

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

if __name__ == "__main__":
    select_words()
    
    
    connection = sqlite3.connect('starwars-comments.txt')
    crsr = connection.cursor()    
    
    rhymeScheme = "ABABCDCDEFEFGG"
    rhymes = dict()
    
    for lineno in range(len(rhymeScheme)):
        line = ""
        lastSyllableStressed = True
        numSyllables = 0
        currentRhyme = rhymeScheme[lineno]

        while numSyllables < 10:
            # choose random words to begin
            word = random.choice(words)
            matching = crsr.execute("select * from words where word=?",
                                 (word,)).fetchall()
            
            # add syllables to lines
            # stressed = 1, unstressed = 0
            for match in matching:
                _, rhym, syls, strs, cmmn = match
                
                # skip if already has more than 10 syllables
                if syls+numSyllables > 10:
                    
                    continue

                # verify stress patterns
                if not stress_pattern(lastSyllableStressed, strs):
                    continue

                # fit rhymes of the last word
                if syls+numSyllables == 10:
                    
                    try:
                        if rhym != rhymes[currentRhyme]:
                            continue
                    except KeyError:
                        rhymes[currentRhyme] = rhym
                        
                line += word+" "
                lastSyllableStressed = strs[-1] == '1'
                numSyllables += syls
                break
       
        # print line              
        print(line)
