import os
import scraping.abbreviations
import scraping.pronunciations
import scraping.words

if __name__ == "__main__":

    # NOTE: Twitter scraping data is in a separate file, as it must be run separately in batches.
    # See twitterScraping.py

    # Make the data directory if it doesn't exist
    if not os.path.isdir("data/"):
        os.makedirs("data")

    ########## GETTING ABBREVIATIONS ##########
    # Gets the OED abbreviations page from the web and parses it into a python dictionary object
    scraping.abbreviations.get_abbreviations()
    # Cleans the abbreviations file
    scraping.abbreviations.clean_abbreviations()

    ########## GETTING PRONUNCIATIONS ##########
    # Get the CMU pronouncing dictionary
    scraping.pronunciations.get_cmudict()
    # Then we do some bash processing to get it into a useful format
    scraping.pronunciations.convert_to_tsv()
    # We convert it into a python dictionary object and save the dictionary as a json file
    scraping.pronunciations.tsv_to_json()
    # We finally clean the messy pronunciations
    scraping.pronunciations.clean_pronunciations()

    ########## GETTING WORDS DICTIONARY ##########
    # Download the dictionary files and merging them
    scraping.words.get_words_file()
    # cleaning up the entries that are phrases or not words by themselves
    scraping.words.clean_dictionary()
