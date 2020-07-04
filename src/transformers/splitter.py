from sklearn.base import TransformerMixin, BaseEstimator


class Splitter(BaseEstimator, TransformerMixin):
    def __init__(self, position):
        self.position = position

    def transform(self, x, y=None):
        content = []
        for sequences in x:
            content.append(sequences[self.position])
        return content


class TupleJoin(TransformerMixin):
    def __init__(self, transformer_list, unpack=None):
        self.unpack = set(unpack) if unpack is not None else set()
        self.transformer_list = transformer_list

    def fit_transform(self, X, y=None, **fit_params):
        return self.transform(X)

    def transform(self, X):
        content = []
        transformers_results = [
            (name, trf.transform(X)) for name, trf in self.transformer_list
        ]
        for row_idx in range(len(X)):
            row_results = []
            for name, results in transformers_results:
                if name in self.unpack:
                    row_results.extend(results[row_idx])
                else:
                    row_results.append(results[row_idx])
            content.append(row_results)
        return content
