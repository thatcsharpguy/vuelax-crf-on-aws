from collections import defaultdict

import joblib


class Tagger:

    labels = {
        "d": "destination",
        "s": "separator",
        "o": "origin",
        "p": "price",
        "f": "flag",
        "n": "irrelevant",
    }

    def __init__(self, pipeline_path):
        self.pipeline = joblib.load(pipeline_path)
        self.tokeniser = self.pipeline.named_steps["tokeniser"]

    def tag(self, text_collection):
        tokens_and_positions = self.tokeniser.transform(text_collection)
        labels = self.pipeline.predict(text_collection)

        return [
            self._merge_by_label(tokens, label)
            for (tokens, _), label in zip(tokens_and_positions, labels)
        ]

    @staticmethod
    def _merge_by_label(tokens, labels):
        content = defaultdict(list)
        for token, label in zip(tokens, labels):
            content[label].append(token)

        return {
            Tagger.labels.get(key): " ".join(value) for key, value in content.items()
        }
