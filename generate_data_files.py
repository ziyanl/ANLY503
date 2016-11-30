import os
import Sonnit.scraping.abbreviations
import Sonnit.scraping.pronunciations
import Sonnit.scraping.words

if __name__ == "__main__":

    # NOTE: Twitter scraping data is in a separate file, as it must be run separately in batches.
    # See twitterScraping.py

    # Make the data directory if it doesn't exist
    if not os.path.isdir("data/"):
        os.makedirs("data")

    ########## GETTING ABBREVIATIONS ##########
    # Gets the OED abbreviations page from the web and parses it into a python dictionary object
    Sonnit.scraping.abbreviations.get_abbreviations()
    # Cleans the abbreviations file
    Sonnit.scraping.abbreviations.clean_abbreviations()

    ########## GETTING PRONUNCIATIONS ##########
    # Get the CMU pronouncing dictionary
    Sonnit.scraping.pronunciations.get_cmudict()
    # Then we do some bash processing to get it into a useful format
    Sonnit.scraping.pronunciations.convert_to_tsv()
    # We convert it into a python dictionary object and save the dictionary as a json file
    Sonnit.scraping.pronunciations.tsv_to_json()
    # We finally clean the messy pronunciations
    Sonnit.scraping.pronunciations.clean_pronunciations()

    ########## GETTING WORDS DICTIONARY ##########
    # Download the dictionary files and merging them
    Sonnit.scraping.words.get_words_file()
    # cleaning up the entries that are phrases or not words by themselves
    Sonnit.scraping.words.clean_dictionary()
