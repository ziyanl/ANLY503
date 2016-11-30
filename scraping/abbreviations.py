import requests
import bs4
import json
import os
import re
import utilities as util


def get_abbreviations():
    """
    Calls to the Oxford English Dictionary abbreviations page and parses out
    the abbreviations into a dictionary of `abbreviation`:`meaning` pairs.

    Also writes the dictionary of abbreviations to a local json file called abbreviations.json in the data folder
    :return: The dictionary of abbreviations
    """
    # We'll use this to store the eventual data
    abbreviations = {}
    # We first get the contents of the page and turn it into a beautiful soup object
    abbreviations_url = "http://public.oed.com/how-to-use-the-oed/abbreviations/"
    req = requests.get(abbreviations_url)
    soup = bs4.BeautifulSoup(req.text)
    # Now we iterate through all of the <tr> tags (table rows) since that's where the abbreviations are
    trs = soup.find_all("tr")
    for tr in trs:
        # We find how many cells are in the row
        tds = tr.find_all("td")
        # If the row doesn't have two cells we skip it
        # because there are some rows with just one cell that
        # act as headers
        if len(tds) == 2:
            abbreviations[tds[0].text] = tds[1].text
    # We save the abbreviations to a file and then return them as well in case the caller wants them right away
    with open(util.path_to_data_directory() + "abbreviations.json", "w") as f:
        json.dump(abbreviations, f)
    return abbreviations


def load_abbreviations():
    """
    Loads the abbreviations file and returns the dictionary
    :return: Abbreviations dictionary of `abbreviation`:`meaning` pairs
    """
    # Check if the file exists
    if os.path.isfile(util.path_to_data_directory() + "abbreviations.json"):
        # The file exists
        with open(util.path_to_data_directory() + "abbreviations.json", "r") as f:
            abbreviations = json.load(f)
    else:
        # The file does not exist
        raise FileNotFoundError(util.path_to_data_directory() +
                                "abbreviations.json doesn't exist. Try get_abbreviations() first.")
    return abbreviations


def clean_abbreviations():
    """
    Loads the abbreviations from disk
    Selects the first word from the potential list of matches:
        "Temp. -> Temporal, Temporary" is converted to "Temp. -> Temporal"
    Gets rid of any optional parts of the abbreviation:
        "Improp. -> Improper(ly)" is converted to "Improp. -> Improper"
    :return:
    """
    abbreviations = load_abbreviations()
    paren_pattern = re.compile("[(]\w+[)]", flags=re.UNICODE)
    for abbreviation in abbreviations:
        # If things are a list of potential matches, take the first one
        if "," in abbreviations[abbreviation]:
            abbreviations[abbreviation] = abbreviations[abbreviation].split(",")[0].strip()
        # Remove everything in parentheses
        abbreviations[abbreviation] = paren_pattern.sub(r'', abbreviations[abbreviation])
    # Convert everything to uppercase
    uppercase_abbreviations = {}
    for abbreviation in abbreviations:
        uppercase_abbreviations[abbreviation.upper()] = abbreviations[abbreviation].upper()
    # Write the new thing to disk so that we don't have to do this again
    with open(util.path_to_data_directory() + "abbreviations.json", "w") as f:
        json.dump(uppercase_abbreviations, f)
    return uppercase_abbreviations


def load_cleaned_abbreviations():
    """
    Cleans up the abbreviations and then returns the cleaned abbreviations dictionary
    :return: The cleaned abbreviations dictionary
    """
    return clean_abbreviations()


def compute_cleanliness_values():
    """
    Computes what percentage of abbreviations don't expand to a single word and will need to be altered
    :return: None, all details are printed out
    """
    # First we get all of the abbreviations into memory
    abbreviations = load_abbreviations()
    # Now we check to see if the expansion of the abbreviation has more than one word in it
    noisy_abbreviations = 0
    for key in abbreviations:
        # If the abbreviation expands to just one word then the length of the split will be 1
        if len(abbreviations[key].split()) != 1:
            noisy_abbreviations += 1
    noise_percentage = noisy_abbreviations / len(abbreviations) * 100
    print("Bad abbreviation records found: " + str(noisy_abbreviations))
    print("Percentage bad abbreviations: " + str(noise_percentage)[:5] + "%")  # [:5] yields 2 decimal places


if __name__ == '__main__':
    get_abbreviations()
