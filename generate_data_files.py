import os
import scraping.abbreviations
import scraping.pronunciations
import scraping.words
import resources

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
    # loads the fully-cleaned CMU dict (only if needed)
    resources.cmudict()
    
    ########## GETTING WORDS DICTIONARY ##########
    # Download the dictionary files and merging them
    scraping.words.get_words_file()
    # cleaning up the entries that are phrases or not words by themselves
    scraping.words.clean_dictionary()
    # generates dict of words that have 1 deletion
    scraping.words.generate_onedel()
