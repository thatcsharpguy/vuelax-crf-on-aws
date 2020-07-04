from pathlib import Path
import os
from nltk import StanfordPOSTagger
from sklearn.base import BaseEstimator, TransformerMixin


class POSTagger(BaseEstimator, TransformerMixin):
    def __init__(self, models_path=None):
        models_path = models_path or os.environ["MODELS_PATH"]
        jar_file = Path(models_path, "stanford-postagger.jar")
        tagger_file = Path(models_path, "spanish.tagger")

        self.tagger = StanfordPOSTagger(str(tagger_file), str(jar_file))

    def tag(self, token_list):
        tags = self.tagger.tag(token_list)
        _, tags = zip(*tags)
        return list(tags)

    def transform(self, x, y=None):
        return [self.tag(sequence) for sequence in x]
