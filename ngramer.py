from collections import deque, defaultdict, Counter
from random import randrange
from nltk import word_tokenize


class Ngramer(object):
    """
    A representation of an n-gram language model.
    """

    START_TOKEN = '<s>'
    END_TOKEN = '</s>'

    def __init__(self, n=2):
        """
        Constructs an Ngramer with the given order n.
        """
        self._n = n
        self._ngrams = defaultdict(Sampler)

    @property
    def n(self):
        """
        The order of the ngramer
        """
        return self._n;

    def update(self, tokens):
        """
        Updates counts based on the provided sequence of tokens.
        Prepends and appends START_TOKEN and END_TOKEN as needed.
        """
        # initialize bounded deque with all <s> tokens
        q = deque([Ngramer.START_TOKEN] * (self._n - 1), maxlen=self._n - 1)

        # build from the tokens
        for token in tokens:
            self._ngrams[tuple(q)].inc(token)
            q.append(token)

        # terminate sequence with </s> token
        self._ngrams[tuple(q)].inc(Ngramer.END_TOKEN)

    def sample(self, prefix):
        """
        Returns a weighted random value given the provided prefix.

        E.g. ngramer.sample(['not', 'the']) == 'droids'
        """
        # Take only the last n-1 tokens, and pad with START_TOKEN if needed
        prefix = prefix[-self._n+1:]
        while len(prefix) < self._n - 1:
            prefix.insert(0, Ngramer.START_TOKEN)

        return self._ngrams[tuple(prefix)].sample()

    def write(self, output):
        """
        Writes ngram model to output stream; used in conjunction with read()
        
        E.g.:
        with open('starwars.ngram', 'w') as f:
            n.write(f)
        """
        for prefix, sampler in self._ngrams.items():
            prefix = ' '.join(prefix)
            for word, count in sampler._weights:
                output.write('{} {} {}\n'.format(prefix, word, count))

    def read(input):
        """
        Reads a build ngram file from input stream; used in conjunction with write()
        
        E.g.:
        with open('starwars.ngram', 'r') as f:
            n = Ngramer.read(f)
        """
        result = Ngramer()
        for line in input:
            line = line.split(' ')
            prefix, word, count = tuple(line[:-2]), line[-2], int(line[-1])
            result._ngrams[prefix]._weights[word] = count
            result._ngrams[prefix]._count += count
        return result
            

    def from_text(lines, n=2, tokenize=word_tokenize):
        """
        Builds an Ngramer based on an iterable list of strings (lines).
        Tokenizes each string based on the tokenize parameter (optional).

        E.g. Ngramer.from_text(open('starwars.txt'))
        """
        result = Ngramer(n)
        for line in lines:
            if line.strip() == '': continue
            result.update(tokenize(line.lower()))
        return result


class Sampler(object):
    """
    Represents an extended Counter that allows random weighed sampling.
    """

    def __init__(self):
        """
        Constructs a new Samplr
        """
        self._count = 0
        self._weights = Counter()

    def inc(self, value):
        """
        Increments the given value, giving it more weight when random sampling
        """
        self._count += 1
        self._weights[value] += 1

    def sample(self):
        """
        Picks a random value based on the weights of each value
        """
        if self._count == 0: return None
        target = randrange(0, self._count)
        c = 0
        for token, count in self._weights.items():
            c += count
            if c > target:
                return token


if __name__ == '__main__':
    """
    Builds an Ngramer from the text in the given file, then generates
    a random sequence based on the model.

    $ python ngramer.py starwars-comments.txt 3
    """
    import sys

    if len(sys.argv) < 3:
        print('args: source_file n')
        exit()

    _, source_file, n = sys.argv
    n = int(n)

    with open(source_file) as f:
        ngramer = Ngramer.from_text(f, int(n))

    c = (n - 1)
    sequence = [Ngramer.START_TOKEN] * c
    while sequence[-1] != Ngramer.END_TOKEN:
        token = ngramer.sample(sequence[-c:])
        sequence.append(token)

    print(' '.join(sequence[c:-1]))
