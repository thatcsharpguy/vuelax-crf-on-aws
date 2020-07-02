from sklearn.base import BaseEstimator, TransformerMixin


class AugmentTokens(BaseEstimator, TransformerMixin):
    def __init__(self, start_tokens, end_tokens, which):
        if isinstance(start_tokens, str):
            start_tokens = [start_tokens]
        if isinstance(end_tokens, str):
            end_tokens = [end_tokens]

        self.return_previous = which == "prev"
        self.start_tokens = start_tokens
        self.end_tokens = end_tokens
        self.skip = len(end_tokens) * 2

    def transform(self, x, y=None):
        return_sequences = []
        for sequence in x:
            return_sequences.append(self.slice_sequence(sequence))
        return return_sequences

    def slice_sequence(self, sequence):
        temporary = self.start_tokens + list(sequence) + self.end_tokens
        part = slice(
            0 if self.return_previous else self.skip,
            len(temporary) - self.skip if self.return_previous else None,
        )
        return temporary[part]
