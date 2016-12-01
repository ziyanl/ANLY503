import json, os
from ngramer import Ngramer
from rhymer import Rhymer
from utilities import mem_cache, fs_cache
import subreddit_scrape
import oov
from text_cleaner import TextCleaner


@mem_cache()
@fs_cache('{}-comments.txt')
def comments(subreddit):
    print('!!! WARNING: starting subreddit scraping. Stop now if not desired.')
    return subreddit_scrape.scrape(subreddit)


@mem_cache()
@fs_cache('{}-comments-clean.txt')
def cleaned_comments(subreddit):
    tc = TextCleaner()
    return [tc.clean_text(line).text for line in comments(subreddit)]


@mem_cache()
@fs_cache('{}.{}gram', Ngramer.read, Ngramer.write)
def ngramer(subreddit, n):
    return Ngramer.from_text(cleaned_comments(subreddit), n)


@mem_cache()
@fs_cache('{}.rhymes', Rhymer.read, Rhymer.write)
def rhymer(subreddit):
    return Rhymer.from_text(cleaned_comments(subreddit))
