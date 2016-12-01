import requests
import urllib.request
import json
import tarfile
import subprocess
import os
import shutil
import utilities as util
from collections import defaultdict


def get_words_file():
    """
    Gets the Moby project's words list files and merges the files into one giant json file
    :return: None
    """
    word_file_url = "http://www.dcs.shef.ac.uk/research/ilash/Moby/mwords.tar.Z"
    word_tar_filename = "words.tar.Z"
    # Clean up any existing dictionaries since they might be modified or otherwise incorrect
    if os.path.isdir(util.path_to_data_directory() + "mwords"):
        shutil.rmtree(util.path_to_data_directory() + "mwords")
    if os.path.isfile(util.path_to_data_directory() + word_tar_filename):
        os.remove(util.path_to_data_directory() + word_tar_filename)
    if os.path.isfile(util.path_to_data_directory() + word_tar_filename[:-2]):
        os.remove(util.path_to_data_directory() + word_tar_filename[:-2])
    # We retrieve the file from the server
    urllib.request.urlretrieve(word_file_url, util.path_to_data_directory() + word_tar_filename)
    # Now we decompress the file
    subprocess.call(["uncompress", util.path_to_data_directory() + word_tar_filename])
    # We open the tar archive
    words_tar = tarfile.open(util.path_to_data_directory() + word_tar_filename[:-2])
    words = []
    # We iterate through all of the files in the archive, skipping `mwords` which is just the folder inside
    for file_info in words_tar.getmembers():
        if file_info.name != "mwords":
            with words_tar.extractfile(file_info) as file:
                # With the extracted file open, read all of the lines and save them to the words list
                for word in file.readlines():
                    words.append(word.decode("latin1"))
    # Save the words to a json file
    with open(util.path_to_data_directory() + "dictionary.json", "w") as dictionary_file:
        json.dump(words, dictionary_file)


def load_dictionary():
    """
    Loads the dictionary.json file and returns the resulting python dictionary
    :return: the dictionary.json file (no guarantee that it's cleaned, run clean_dictionary() to be sure)
    """
    dictionary_filename = "dictionary.json"
    with open(util.path_to_data_directory() + dictionary_filename) as dictionary_file:
        words = json.load(dictionary_file)
    return words


def clean_dictionary():
    """
    Opens the dictionary.json file, removes duplicate entries and entries that aren't single words
    Writes the cleaned dictionary back into dictionary.json
    :return: The cleaned dictionary as a list
    """
    dictionary_filename = "dictionary.json"
    words = load_dictionary()
    final_words = set()
    for word in words:
        # We check to see if the line has more than one word on it
        # If it does, then it's a phrase or non-word
        if len(word.split()) == 1:
            # We add the words in all lowercase because capitalization will not
            # matter for what we are going to study
            # We also strip off newline characters
            final_words.add(word.lower().strip())
    # We convert the set into a list so that we can dump it to json
    final_words = list(final_words)
    # Convert everything to uppercase
    final_words_uppercase = set()
    for word in final_words:
        final_words_uppercase.add(word.upper())
    with open(util.path_to_data_directory() + dictionary_filename, "w") as dictionary_file:
        json.dump(list(final_words_uppercase), dictionary_file)
    return final_words_uppercase


def load_cleaned_dictionary():
    """
    Cleans the dictionary and then returns the cleaned dictionary
    :return: The cleaned dictionary
    """
    return clean_dictionary()


def compute_cleanliness_values():
    """
    Calculates how many duplicates, phrases, and overal junk values were present in the initial dictionary files
    :return: None, all values are printed to stdout
    """
    # We regenerate the data so that we can see how much it was reduced by
    get_words_file()
    # We see how many entries we had to start
    starting_dictionary = load_dictionary()
    start_len = len(starting_dictionary)
    # Next let's see how many duplicates we have
    duplicates = start_len - len(set(starting_dictionary))
    # We compute the percentage of duplicates
    duplicates_percentage = duplicates / start_len * 100
    # Now we count how many values are phrases
    phrases = 0
    for word in starting_dictionary:
        # Any single word would have a length of 1 here
        if len(word.split()) != 1:
            phrases += 1
    # We compute percentage of phrases
    phrases_percentage = phrases / start_len * 100
    # We clean the dictionary
    # We see how many entries are in the cleaned data
    clean_len = len(clean_dictionary())
    # We compute the number of overall junk values
    junk_values = start_len - clean_len
    junk_values_percentage = junk_values / start_len * 100
    # We display the results
    print("Duplicates found: " + str(duplicates))
    print("Percentage duplicates: " + str(duplicates_percentage)[:5] + "%")  # [:5] yields 2 decimal places
    print("Phrases found: " + str(phrases))
    print("Percentage phrases: " + str(phrases_percentage)[:5] + "%")
    print("Total number of junk values: " + str(junk_values))
    print("Percentage junk values: " + str(junk_values_percentage)[:5] + "%")


def load_onedel():
    """
    Loads the dictionary-onedel.json file and returns the resulting python dictionary
    :return: the dictionary-onedel.json file
    """
    dictionary_filename = "dictionary-onedel.json"
    with open(util.path_to_data_directory() + dictionary_filename) as dictionary_file:
        words = json.load(dictionary_file)
    return words

def generate_onedel():
    """
    Generates the dictionary-onedel.json file and returns the resulting python dictionary
    :return: the dictionary-onedel.json file
    """
    d = load_cleaned_dictionary()
    result = defaultdict(list)
    for word in d:
        variations = set((word[:i]+word[i+1:] for i in range(1, len(word)-1)))
        for variation in variations:
            result[variation].append(word)

    dictionary_filename = "dictionary-onedel.json"
    with open(util.path_to_data_directory() + dictionary_filename, 'w') as dictionary_file:
        words = json.dump(result, dictionary_file)
    return result

if __name__ == "__main__":
    get_words_file()
    print(len(load_dictionary()))
    cleaned = clean_dictionary()
