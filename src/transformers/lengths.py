from sklearn.base import BaseEstimator, TransformerMixin


class TokenLength(BaseEstimator, TransformerMixin):
    def transform(self, x, y=None):
        return [[len(token) for token in sequence] for sequence in x]


class TokenListLength(BaseEstimator, TransformerMixin):
    def transform(self, x, y=None):
        return [[len(sequence) for _ in sequence] for sequence in x]
