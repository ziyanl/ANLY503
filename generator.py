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
