from collections import defaultdict
import random
from nltk import word_tokenize
import oov

class Rhymer(object):
    def __init__(self, CMUDICT):
        """
        Constructs an Ngramer with the given order n.
        """
        self._rhyme_classes = defaultdict(set)
        self._cache = {}
        self.CMUDICT = CMUDICT

    def _get_rhyme(self, pron):
        '''
        :param pron: pronunciation of a word
        :return: list of phonemes representing the end of the word starting with the last stressed vowel
        '''
        rhyme = []
        for phon in pron[::-1]:
            rhyme.insert(0, phon)
            if phon[-1] == '1':
                return rhyme
        return rhyme

    def _get_rhyme_tuple(self, token):
        if token not in self._cache:
            self._cache[token] = tuple(self._get_rhyme(oov.guess_pron(token, CMUDICT=self.CMUDICT)))
        return self._cache[token]

    def update(self, tokens):
        # build from the tokens
        for token in tokens:
            self._rhyme_classes[self._get_rhyme_tuple(token)].add(token)

    def sample(self, word):
        words = self._rhyme_classes[self._get_rhyme_tuple(word)]
        if len(words) <= 1:
            return word
        return random.choice(tuple(words  - {word}))

    def write(self, output):
        for rhyme, words in self._rhyme_classes.items():
            output.write('{}\t{}\n'.format(' '.join(rhyme), ' '.join(words)))

    def read(input, CMUDICT):
        result = Rhymer(CMUDICT)
        for line in input:
            rhyme, words = line.split('\t')
            rhyme = tuple(rhyme.split(' '))
            words = set(words.split(' '))
            result._rhyme_classes[rhyme] = words
        return result

    def from_text(lines, CMUDICT, tokenize=word_tokenize):
        result = Rhymer(CMUDICT)
        for line in lines:
            if line.strip() == '': continue
            result.update(tokenize(line.upper()))
        return result
