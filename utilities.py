import os


def path_to_data_directory():
    """
    Searches downward from wherever is defined as "__main__" to find a `data` folder
    :return: The relative path to the data folder
    """
    path = "data/"
    layers = 1
    while not os.path.isdir(path):
        path = "../" + path
        layers += 1
        if layers > 100:
            # We are far too far away from the project and the data folder
            # likely doesn't exist. Raise and error to prevent an infinite loop
            raise FileNotFoundError("The data directory could not be found. Are you sure it exists?")
    return path


def path_to_scraping_directory():
    """
    Determines whether we are in the scraping directory or one layer above it
    :return: The relative path to the scraping directory
    """
    # If scraping/ exists then we are outside of the folder
    if os.path.isdir("scraping/"):
        path = "scraping/"
    else:
        # Otherwise we are inside of the scraping directory
        path = ""
    return path

class TextStatistics:
    """Used to store a text and its cleaning information"""

    def __init__(self, text):
        self.original_text = text
        self.text = text
        self.emoji_count = 0
        self.hashtag_count = 0
        self.handle_count = 0
        self.url_count = 0
        self.abbreviation_count = 0
        self.punctuation_count = 0
        self.misspellings_count = 0
