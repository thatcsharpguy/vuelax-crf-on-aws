from sklearn.base import BaseEstimator, TransformerMixin


class TextTransform(BaseEstimator, TransformerMixin):
    def __init__(self, text_transform_function):
        self.transform_function = text_transform_function

    def transform(self, x, y=None):
        return [
            [self.transform_function(token) for token in sequence] for sequence in x
        ]
