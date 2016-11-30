# -*- coding: utf-8 -*-
#!/usr/bin/python

import re
#import sys
import random
import sqlite3

global wordlist
repeat = re.compile("[A-Z']*\\([0-9]+\\)")
whitespace = re.compile("\\s+")

# function for removing whitespace in lines
def split_line(line):
    syllables = filter(None, whitespace.split(line))
    return ' '.join(syllables)

def init_wordlist():
    global wordlist
    wordlist = []
    with open('cmudict_0.7b.txt','r') as file:
        for line in file:
            line = split_line(line)
            # skip comments and line not beginning with letter
            if not line[0].isalpha():
                continue

            syllables = line.split(' ', 1)
            word = syllables[0]
            if repeat.match(word):
                continue
            # append word not in wordlist
            wordlist.append(word)

# function for stress pattern verification
def stress_pattern(stressed, s):
    nums = [1 if stressed else 0]
    for count in s:
        nums.append(int(count))        
    bad = False
    for i in xrange(len(nums) - 1):
        if nums[i] == nums[i + 1]:
            bad = True
            break
    return not bad

def get_stress_pattern(p):
    nums = []
    for c in p:
        if c.isdigit():
            nums.append(1 if int(c)>0 else 0)
    return nums

if __name__ == "__main__":
    select_words()
    rhymeScheme = "ABABCDCDEFEFGG"
    rhymes = dict()
    
    for lineno in range(len(rhymeScheme)):
        line = ""
        lastSyllableStressed = True
        numSyllables = 0
        currentRhyme = rhymeScheme[lineno]

        while numSyllables < 10:
            word = random.choice(words)
            matching = c.execute("select * from words where word=?",
                                 (word,)).fetchall()
            
            for match in matching:
                _, rhym, syls, strs, cmmn = match
                
                if syls+numSyllables > 10:
                    # This pronunciation is too long. Skip.
                    continue

                # Verify stress patterns
                if not stress_pattern(lastSyllableStressed,strs):
                    continue

                if syls+numSyllables == 10:
                    # We get the last word in this! Deal with rhymes
                    try:
                        if rhym != rhymes[currentRhyme]:
                            continue
                    except KeyError:
                        rhymes[currentRhyme] = rhym
                        
                line += word+" "
                lastSyllableStressed = strs[-1] == '1'
                numSyllables += syls
                break

        print(line)
