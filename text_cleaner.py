from collections import Counter
import re
import nltk
import scraping.abbreviations as abbrev
import scraping.words as dictionary
import utilities as util


class TweetCleaner:
    def __init__(self):
        ### Load our abbreviation dictionary
        self.abbreviations = abbrev.load_cleaned_abbreviations()
        ### Load our normal dictionary
        self.dictionary = dictionary.load_cleaned_dictionary()
        ### Load the Brown corpus for spelling correction
        # First download the corpus if we don't have it
        nltk.download('brown')
        # Get the words from the corpus
        brown_words = nltk.corpus.brown.words()
        # Get the count of their occurances
        word_counts = Counter()
        for word in brown_words:
            word_counts[word] += 1
        # Compute their prior probabilities
        self.prior_word_probabilites = {}
        brown_words_len = len(brown_words)
        for word in word_counts:
            self.prior_word_probabilites[word] = word_counts[word] / brown_words_len
        # Create our tweet tokenizer so we don't have to make it over and over again
        self.tweet_tokenizer = nltk.tokenize.TweetTokenizer()

    def clean_tweet(self, tweet_text):
        """
        Removes emojis, hashtags, handles, URLs, abbreviations, punctuation, and misspellings from a tweet's text
        :param tweet_text: The tweet text to clean up
        :return: A Tweet object with the original text, the cleaned text, and cleaning statistics
        """
        tweet = util.TweetStatistics(tweet_text)
        # We now clean the tweets of all of their non-word features
        # NOTE: The order of these calls is VERY important
        # Do NOT rearrange the call sequence
        tweet_text = tweet_text.upper()
        tweet_text, emoji_count = self._remove_emojis(tweet_text)
        tweet_text, hashtag_count = self._remove_hashtags(tweet_text)
        tweet_text, handle_count = self._remove_handles(tweet_text)
        tweet_text, url_count = self._remove_urls(tweet_text)
        tweet_text, abbreviation_count = self._remove_abbreviations(tweet_text)
        tweet_text, punctuation_count = self._remove_punctuation(tweet_text)
        tweet_text, misspellings_count = self._remove_misspellings(tweet_text)
        # Save all of these values into our Tweet data structure
        tweet.text = tweet_text
        tweet.emoji_count = emoji_count
        tweet.hashtag_count = hashtag_count
        tweet.handle_count = handle_count
        tweet.url_count = url_count
        tweet.abbreviation_count = abbreviation_count
        tweet.punctuation_count = punctuation_count
        tweet.misspellings_count = misspellings_count
        return tweet

    def _remove_emojis(self, tweet):
        """Removes all of the emoji characters and returns the cleaned up tweet
        and the count of the number of emojis removed

        Help taken from: http://stackoverflow.com/questions/33404752/removing-emojis-from-a-string-in-python

        :param tweet: The tweet text to clean
        :return: Cleaned tweet text and count of emojis removed
        """
        emoji_pattern = re.compile("["
                                   u"\U0001F600-\U0001F64F"  # emoticons
                                   u"\U0001F300-\U0001F5FF"  # symbols & pictographs
                                   u"\U0001F680-\U0001F6FF"  # transport & map symbols
                                   u"\U0001F1E0-\U0001F1FF"  # flags (iOS)
                                   "]+", flags=re.UNICODE)
        # First we count how many emojis are present in the text
        emoji_count = len(emoji_pattern.findall(tweet))
        # Now we swap out all of the emojis
        cleaned_tweet = emoji_pattern.sub(r'', tweet)
        return cleaned_tweet, emoji_count

    def _remove_hashtags(self, tweet):
        """
        Iterates through the tweet text parts and attempts to resolve hashtags into actual words.
        If the hashtag cannot be resolved into words then it is removed from the text
        :param tweet: The tweet text to remove hashtags from
        :return: The hashtag free text as well as the number of hashtags removed
        """
        hashtag_pattern = re.compile("[#]\w+", flags=re.UNICODE)
        tweet_parts = self.tweet_tokenizer.tokenize(tweet)
        filtered_tweet_parts = []
        hashtag_count = 0
        for element in tweet_parts:
            if element.startswith("#"):
                hashtag_count += 1
                # Cut off the "#"
                element = element[1:]
                # Check to see if the hashtag is a word by itself
                if element in self.dictionary:
                    # Nothing else to do so move on
                    continue
                # Otherwise check to see if inserting a space anywhere can make it two valid words
                for i in range(1, len(element) - 1):
                    word1 = element[:i]
                    word2 = element[i:]
                    if word1 in self.dictionary and word2 in self.dictionary:
                        filtered_tweet_parts.append(word1)
                        filtered_tweet_parts.append(word2)
                        break
                        # If adding one space couldn't save us then just skip the hashtag
            else:
                filtered_tweet_parts.append(element)
        return " ".join(filtered_tweet_parts), hashtag_count

    def _remove_punctuation(self, tweet):
        """
        Filters out punctuation marks from the tweet text.
        NB: For our sake any numbers in the text are considered punctuation marks
        NB: This will remove text like "2pac" and ":-)" as one punctuation mark
        :param tweet: The tweet text to clean
        :return: The tweet text with punctuation removed and the number of punctuation marks removed
        """
        # We have to include "_" as its own category because it is considered a word character in some versions of regex
        punctuation_pattern = re.compile("\W|_")
        number_pattern = re.compile("\d")
        punctuation_count = 0
        tweet_parts = self.tweet_tokenizer.tokenize(tweet)
        filtered_tweet_parts = []
        for element in tweet_parts:
            # If it's a word containing punctuation just move on
            if element in self.dictionary:
                filtered_tweet_parts.append(element)
                continue
            # We only keep those parts that don't contain any punctuation or numbers
            if len(punctuation_pattern.findall(element)) == 0 and len(number_pattern.findall(element)) == 0:
                filtered_tweet_parts.append(element)
            else:
                punctuation_count += 1
        return " ".join(filtered_tweet_parts), punctuation_count

    def _remove_handles(self, tweet):
        """
        Removes twitter "@ mentions" aka "handles" from the tweet text
        :param tweet: The text to clean up
        :return: The handle scrubbed text as well as the number of handles removed
        """
        handle_pattern = re.compile("[@]\w+", flags=re.UNICODE)
        handle_count = len(handle_pattern.findall(tweet))
        # Now remove them
        cleaned_tweet = handle_pattern.sub(r'', tweet)
        return cleaned_tweet, handle_count

    def _remove_urls(self, tweet):
        """Removes URLs to the best of its abilities
        Regex modified from: https://github.com/django/django/blob/1.6/django/core/validators.py#L43-50

        :param tweet: The tweet text to clean
        :return:
        """
        url_pattern = re.compile(
            r'(?:^(?:http|ftp)s?://)?'  # http:// or https://
            r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?)|'  # domain...
            r'localhost|'  # localhost...
            r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}|'  # ...or ipv4
            r'\[?[A-F0-9]*:[A-F0-9:]+\]?)'  # ...or ipv6
            r'(?::\d+)?'  # optional port
            r'(?:/?|[/?]\S+)\b', re.IGNORECASE)
        url_count = len(url_pattern.findall(tweet))
        cleaned_tweet = url_pattern.sub(r'', tweet)
        return cleaned_tweet, url_count

    def _remove_abbreviations(self, tweet):
        """
        Iterates through the tweet text to find abbreviations and replace them if possible
        If an abbreviation cannot be replaced then it is removed from the text
        :param tweet: The tweet text to look through
        :return: The abbreviation corrected tweet text as well as the number of abbreviations removed
        """
        abbreviation_count = 0
        tweet_parts = self.tweet_tokenizer.tokenize(tweet)
        expanded_tweet_parts = []
        i = 0
        # We scan through our parts seeing if any words followed by a "." are in our abbreviation dictionary
        while i < len(tweet_parts):
            try:
                abbreviation = "".join([tweet_parts[i], tweet_parts[i + 1]])
                if abbreviation in self.abbreviations:
                    expanded_tweet_parts.append(self.abbreviations[abbreviation])
                    abbreviation_count += 1
                    i += 2
                else:
                    expanded_tweet_parts.append(tweet_parts[i])
                    i += 1
            except IndexError:
                # If we have triggered the IndexError then we are at the end of the sentence
                expanded_tweet_parts.append(tweet_parts[i])
                i += 1
        return " ".join(expanded_tweet_parts), abbreviation_count

    def _remove_misspellings(self, tweet):
        """
        Iterates through all of the words in the tweet and corrects misspellings to the best of its ability
        :param tweet: The text to spell check
        :return: The spelling corrected tweet text and the number of misspellings
        """
        misspellings_count = 0
        tweet_parts = self.tweet_tokenizer.tokenize(tweet)
        corrected_tweet_parts = []
        for word in tweet_parts:
            corrected_word = self.correct_spelling(word)
            if corrected_word != word:
                corrected_tweet_parts.append(corrected_word)
                misspellings_count += 1
            else:
                corrected_tweet_parts.append(word)
        return " ".join(corrected_tweet_parts), misspellings_count

    def correct_spelling(self, word):
        """
        If the specified word is in our dictionary return the word
        Otherwise make a probabilistic prediction about what the word should be

        Spelling correction model taken from here: http://norvig.com/spell-correct.html
        :param word:
        :return: The probabilistically corrected spelling of the word if the word is not in our dictionary
        """
        if word in self.dictionary:
            return word
        # Otherwise correct it probabilistically
        return self._correction(word)

    def _P(self, word):
        """
        Returns the prior probability of a specified word
        :param word: The word to get the prior probability for
        :return: The prior probability for that word, 0 if it has never been seen before
        """
        return self.prior_word_probabilites.get(word, 0)

    def _correction(self, word):
        """
        Determines the most probable spelling correction for a word
        :param word: The word to spelling correct
        :return: The most probable spelling correction for the word
        """
        "Most probable spelling correction for word."
        # sorted(list()) is used to enforce deterministic spellling corrections
        return max(sorted(list(self._candidates(word))), key=self._P)

    def _candidates(self, word):
        """
        Determines the possible candidates spelling corrections for a word
        Prioritizes returning the original word if spelled correctly, followed by words 1 edit away,
        then words 2 edits away, and finally the original word if spelled incorrectly and uncorrectable
        :param word: The word to generate candidates for
        :return: The best set of candidates
        """
        return (self._known([word]) or self._known(self._edits1(word)) or self._known(self._edits2(word)) or [word])

    def _known(self, words):
        """
        Determines the subset of the supplied list of words that are present in the dictionary
        :param words: The list of words to check
        :return: The set of words that were present in the dictionary
        """
        return set(w for w in words if w in self.dictionary)

    def _edits1(self, word):
        """
        Computes all words that are one "edit" away from the given word
        An edit is defined as a character deletion, a transposition, a character replacement, or a character insert
        :param word: The word to calculate edits for
        :return: The list of words 1 edit away
        """
        letters = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
        splits = [(word[:i], word[i:]) for i in range(len(word) + 1)]
        deletes = [L + R[1:] for L, R in splits if R]
        transposes = [L + R[1] + R[0] + R[2:] for L, R in splits if len(R) > 1]
        replaces = [L + c + R[1:] for L, R in splits if R for c in letters]
        inserts = [L + c + R for L, R in splits for c in letters]
        return set(deletes + transposes + replaces + inserts)

    def _edits2(self, word):
        """
        Computes all words that are 2 edits away. See "_edits1" for the definition of an edit
        :param word: The word to calculate edits for
        :return: The list of words 2 edits away
        """
        return (e2 for e1 in self._edits1(word) for e2 in self._edits1(e1))
