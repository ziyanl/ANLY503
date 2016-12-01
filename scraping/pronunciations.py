import requests
import subprocess
import os
import stat
import json
import utilities as util
import resources


def get_cmudict():
    """
    Fetches the CMU pronunciations dictionary from their servers and returns the text (split by line)
    :return: list of lines in cmudict
    """
    req = requests.get("http://svn.code.sf.net/p/cmusphinx/code/trunk/cmudict/cmudict-0.7b")
    with open(util.path_to_data_directory() + "cmudict-07.b", "w") as f:
        return req.text.split('\n')


def convert_to_tsv(txt_lines):
    """
    Converts the CMU pronunciations dictionary into a tab separated values (TSV) file for easier processing
    Also gets rid of all lines that don't correspond to words
    :return: List of tuples representing each valid line in the file (word, number, pron)
    """
    for line in txt_lines:
        if re.match('[A-Z]', line) is not None:
            m = re.match(r'([^( ]+)(\([0-9]+\))?[ ]+(.*)$', line)
            yield m.group(1), m.group(2) or '', m.group(3)


def tsv_to_json(tsv_lines):
    """
    Loads the TSV file and produces a dictionary of `word`:`[prounciations]` pairs
    Saves the dictionary object to pronunciations.json
    :return: The python dictionary of `word`:`[prounciations]` pairs
    """
    words = {}
    for word, index, pron in tsv_lines:
        pronunciation = pronunciation.split()
        if word in words:
            words[word].append(pronunciation)
        else:
            words[word] = [pronunciation]
    return words


def load_pronunciations():
    """
    Loads the pronunciations dictionary from pronunciations.json and returns it
    :return: The pronunciations dictionary
    """
    with open(util.path_to_data_directory() + "pronunciations.json", "r") as prounciations_file:
        pronunciations = json.load(prounciations_file)
    return pronunciations


def clean_pronunciations(pronunciations):
    """
    Converts the pronunciations by selecting the first pronunciation out of the list of possible matches
    Ex: "REARVIEW": [["R", "IH1", "R", "V", "Y", "UW0"], ["R", "IY1", "R", "V", "Y", "UW0"]]"
        goes to
        "REARVIEW": ["R", "IH1", "R", "V", "Y", "UW0"]"
    :return: A dictionary of `word`:`pronunciation` pairs
    """
    for pronunciation in pronunciations:
        pronunciations[pronunciation] = pronunciations[pronunciation][0]
    # Return them so that other people can clean and get at the same time
    return pronunciations


def compute_cleanliness_values():
    """
    Computes how many known words can be pronounced more than one way
    :return: None, prints out the details
    """
    # We load the pronunciations
    pronunciations = resources.cmudict_json()
    ambiguous_pronunciations = 0
    for word in pronunciations:
        # If the length of the pronunciations list for the word is greater than 1 then its ambiguous
        if len(pronunciations[word]) > 1:
            ambiguous_pronunciations += 1
    # We compute the percentage of pronunciations which are ambiguous
    ambiguous_pronunciations_percentage = ambiguous_pronunciations / len(pronunciations) * 100
    print("Number of ambiguous pronunciations: " + str(ambiguous_pronunciations))
    print("Percentage ambiguous pronunciations: " + str(ambiguous_pronunciations_percentage)[:5] + "%")
    # [:5] yields 2 decimal places

