from collections import deque, defaultdict, Counter
from random import randrange
from nltk import word_tokenize

DEFAULT_N = 2

class Ngramer(object):
    """
    A representation of an n-gram language model.
    """

    START_TOKEN = '<S>'
    END_TOKEN = '</S>'

    def __init__(self, n=DEFAULT_N):
        """
        Constructs an Ngramer with the given order n.
        """
        self._n = n
        self._ngrams = Counter()
        self._samplers = defaultdict(Sampler)

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
        q = deque([Ngramer.START_TOKEN] * self._n, maxlen=self._n)

        # build from the tokens
        for token in tokens:
            q.append(token)
            self._ngrams[tuple(q)] += 1
            r = list(q)
            for i in range(self._n):
                partial = tuple(r[:i] + [...] + r[i+1:])
                self._samplers[partial].inc(r[i])

        # terminate sequence with </s> token
        q.append(Ngramer.END_TOKEN)
        self._ngrams[tuple(q)] += 1
        r = list(q)
        for i in range(self._n):
            partial = tuple(r[:i] + [...] + r[i+1:])
            self._samplers[partial].inc(r[i])

    def sample(self, pattern):
        """
        Returns a weighted random value given the provided pattern.
        An ellipsis is used to represent the value to sample, e.g. ['hello', ...] or
        ['these', 'are', ..., 'the', 'droids']. If a pattern is too long,
        for the n value, initial values are ignored. If no ellipsis is present, it
        is assumed to end in an ellipsis. If it is too short, start tokens are assumed.

        E.g. ngramer.sample(['not', 'the', ...]) == 'droids'
        """
        # Append ... if not included in pattern
        if Ellipsis not in pattern:
            pattern = pattern + [...]

        # Take only the last n tokens
        pattern = pattern[-self._n:]

        # Pad with <s> if not long enough
        pattern = [Ngramer.START_TOKEN] * (self._n - len(pattern)) + pattern
        
        # Sample the distribution
        return self._samplers[tuple(pattern)].sample()

    def write(self, output):
        """
        Writes ngram model to output stream; used in conjunction with read()
        
        E.g.:
        with open('starwars.ngram', 'w') as f:
            n.write(f)
        """
        for ngram, count in self._ngrams.items():
            output.write('{} {}\n'.format(' '.join(ngram), count))

    def read(input, n=DEFAULT_N):
        """
        Reads a build ngram file from input stream; used in conjunction with write()
        
        E.g.:
        with open('starwars.ngram', 'r') as f:
            n = Ngramer.read(f)
        """
        result = Ngramer(n)
        for line in input:
            line = line.split(' ')
            ngram, count = tuple(line[:-1]), int(line[-1])
            result._ngrams[ngram] = count
            r = list(ngram)
            for i in range(result._n):
                partial = tuple(r[:i] + [...] + r[i+1:])
                result._samplers[partial].set(ngram[i], count)
        return result
            

    def from_text(lines, n=DEFAULT_N, tokenize=word_tokenize):
        """
        Builds an Ngramer based on an iterable list of strings (lines).
        Tokenizes each string based on the tokenize parameter (optional).

        E.g. Ngramer.from_text(open('starwars.txt'))
        """
        result = Ngramer(n)
        for line in lines:
            if line.strip() == '': continue
            result.update(tokenize(line.upper()))
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

    def inc(self, token):
        """
        Increments the given token, giving it more weight when random sampling
        """
        self._count += 1
        self._weights[token] += 1

    def set(self, token, count):
        """
        Sets the given token count
        """
        self._count += count - self._weights[token]
        self._weights[token] = count

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
