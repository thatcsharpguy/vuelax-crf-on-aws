from nltk import TweetTokenizer
from sklearn.base import BaseEstimator, TransformerMixin


class Tokeniser(BaseEstimator, TransformerMixin):
    def __init__(self, return_flags=False):
        self.tokeniser = TweetTokenizer()
        self.return_flags = return_flags

    def fit(self, *args, **kwargs):
        return self

    def tokenise(self, sequence):
        flag = ""
        ix = 0
        tokens, positions = [], []
        for t in self.tokeniser.tokenize(sequence):
            ix = sequence.find(t, ix)
            if len(t) == 1 and ord(t) >= 127462:  # this is the code for 🇦
                if not self.return_flags:
                    continue
                if flag:
                    tokens.append(flag + t)
                    positions.append(ix - 1)
                    flag = ""
                else:
                    flag = t
            else:
                tokens.append(t)
                positions.append(ix)
            ix = +1
        return tokens, positions

    def transform(self, x, y=None):
        return [self.tokenise(sequence) for sequence in x]
