import requests
import subprocess
import os
import stat
import json
import utilities as util


def get_cmudict():
    """
    Fetches the CMU pronunciations dictionary from their servers and saves it to the data directory
    :return:
    """
    req = requests.get("http://svn.code.sf.net/p/cmusphinx/code/trunk/cmudict/cmudict-0.7b")
    with open(util.path_to_data_directory() + "cmudict-07.b", "w") as f:
        f.write(req.text)


def convert_to_tsv():
    """
    Converts the CMU pronunciations dictionary into a tab separated values (TSV) file for easier processing
    Also gets rid of all lines that don't correspond to words
    Achieves this through the use of a shell script that invokes some regex magic
    :return: None, the new file is simply saved to the data directory
    """
    if os.path.isfile(util.path_to_data_directory() + "cmudict-07.b"):
        # First ensure that the script is executable
        # Credit goes to http://stackoverflow.com/questions/12791997/how-do-you-do-a-simple-chmod-x-from-within-python
        st = os.stat(util.path_to_scraping_directory() + 'cmudict_to_tsv.sh')
        os.chmod(util.path_to_scraping_directory() + 'cmudict_to_tsv.sh', st.st_mode | stat.S_IEXEC)
        # Now we execute the conversion script
        subprocess.call(['./' + util.path_to_scraping_directory() + 'cmudict_to_tsv.sh'])
    else:
        raise FileNotFoundError(util.path_to_data_directory() + "cmudict-07.b does not exist. Try running get_cmudict()")


def tsv_to_json():
    """
    Loads the TSV file and produces a dictionary of `word`:`[prounciations]` pairs
    Saves the dictionary object to pronunciations.json
    :return: The python dictionary of `word`:`[prounciations]` pairs
    """
    words = {}
    with open(util.path_to_data_directory() + "cmudict.tsv", 'r', encoding='latin-1') as tsv:
        for line in tsv:
            parts = line.split()
            word = parts[0]
            if parts[1].startswith("("):
                # In this case it is an alternate pronunciation
                pronunciation = parts[2:]
            else:
                pronunciation = parts[1:]
            if word in words:
                words[word].append(pronunciation)
            else:
                words[word] = [pronunciation]
    with open(util.path_to_data_directory() + "pronunciations.json", "w") as f:
        json.dump(words, f)
    return words


def load_pronunciations():
    """
    Loads the pronunciations dictionary from pronunciations.json and returns it
    :return: The pronunciations dictionary
    """
    with open(util.path_to_data_directory() + "pronunciations.json", "r") as prounciations_file:
        pronunciations = json.load(prounciations_file)
    return pronunciations


def clean_pronunciations():
    """
    Cleans the pronunciations by selecting the first pronunciation out of the list of possible matches
    Ex: "REARVIEW": [["R", "IH1", "R", "V", "Y", "UW0"], ["R", "IY1", "R", "V", "Y", "UW0"]]"
        goes to
        "REARVIEW": ["R", "IH1", "R", "V", "Y", "UW0"]"
    :return:
    """
    pronunciations = load_pronunciations()
    # Check to see if we have already cleaned this data before
    # If any of the words have more than 5 "pronunciations" associated with them then
    # don't clean it any more because it's already cleaned
    for pronunciation in pronunciations:
        if len(pronunciations[pronunciation]) > 5:
            return pronunciations
    for pronunciation in pronunciations:
        pronunciations[pronunciation] = pronunciations[pronunciation][0]
    # Save the updated pronunciations list to disk
    with open(util.path_to_data_directory() + "pronunciations.json", "w") as f:
        json.dump(pronunciations, f)
    # Return them so that other people can clean and get at the same time
    return pronunciations


def compute_cleanliness_values():
    """
    Computes how many known words can be pronounced more than one way
    :return: None, prints out the details
    """
    # We load the pronunciations
    pronunciations = load_pronunciations()
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


if __name__ == "__main__":
    get_cmudict()
    convert_to_tsv()
    tsv_to_json()
