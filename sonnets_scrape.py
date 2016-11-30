from bs4 import BeautifulSoup
import re, json, os


def scrape(sonnets_dir):
    """
    Scrapes sonnet lines from the sonnets.org corpus
    """

    # Get list of sonnet files
    pages = os.listdir(sonnets_dir)

    for page in pages:
        # load page HTML
        with open(os.path.join(sonnets_dir, page), encoding='latin_1') as f:
            page_html = f.read()

        # BeautifulSoup doesn't work well here because of the terribly-formatted HTML.
        # Re sort to just using regex rules.
        state = None
        for line in page_html.split('\n'):
            line = line.strip()

            # Detect a new sonnet and get its title
            title = re.search('<h2>([^>]+)</h2>', line)
            if title != None:
                state = 'POEM'
                title_text = strip_tags(title.group(1)).strip()

            if state == 'POEM':
                # Get the line from the sonnet
                poem_line = re.search('<dt>(.+)', line)
                if poem_line != None:
                    yield strip_tags(poem_line.group(1)).strip()


def strip_tags(html):
    """
    Removes HTML tags from the provided text
    """
    return BeautifulSoup(html, "lxml").get_text()


if __name__ == '__main__':
    """
    Writes lines from sonnets in the provided directory to stdout

    $ python subreddit_scrape.py /data/sonnets.org > sonnet-lines.txt
    """
    import sys

    if len(sys.argv) < 2:
        print('args: sonnets_dir')
        exit()

    for sonnet_line in scrape(sys.argv[1]):
        print(sonnet_line)
