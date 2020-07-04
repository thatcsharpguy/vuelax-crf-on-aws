import os
from sklearn.pipeline import Pipeline, FeatureUnion

from transformers import (
    Tokeniser,
    Splitter,
    POSTagger,
    TokenLength,
    TokenListLength,
    AugmentTokens,
    TextTransform,
    FeaturiseCRF,
)
from transformers.splitter import TupleJoin
from transformers.utils import is_punctuation, is_numeric

MODELS_PATH = os.getenv("MODELS_PATH")

previous_next_pos = TupleJoin(
    [
        (
            "prev_pos",
            AugmentTokens(start_tokens="<p>", end_tokens="</p>", which="prev"),
        ),
        (
            "next_pos",
            AugmentTokens(start_tokens="<p>", end_tokens="</p>", which="next"),
        ),
    ]
)

pos_pipeline = Pipeline(
    [
        ("pos_tags", POSTagger(MODELS_PATH)),
        ("prev_next_pos", previous_next_pos),
        ("x", "passthrough"),
    ]
)

other_features = TupleJoin(
    [
        ("current_uppercase", TextTransform(str.upper)),
        ("current_lowercase", TextTransform(str.lower)),
        ("is_punctuation", TextTransform(is_punctuation)),
        ("is_numeric", TextTransform(is_numeric)),
        ("token_lengths", TokenLength()),
        ("sentence_length", TokenListLength()),
        ("pos_tags", POSTagger(MODELS_PATH)),
        ("pos", pos_pipeline),
    ],
    unpack=["pos"],
)

other = Pipeline(
    [
        ("select_tokens", Splitter(0)),
        ("other_features", other_features),
        ("x", "passthrough"),
    ]
)

union = TupleJoin(
    [("positions", Splitter(1)), ("tokens", Splitter(0)), ("other", other)],
    unpack=["other"],
)

text = Pipeline(
    [
        ("selector", Tokeniser()),
        ("only_tokens", union),
        (
            "featurise",
            FeaturiseCRF(
                feature_order=[
                    "position",
                    "original",
                    "upper",
                    "lower",
                    "is_punctuation",
                    "is_numeric",
                    "token_lengths",
                    "sentence_lengths",
                    "pos",
                    "prev_pos",
                    "next_pos",
                ],
                shared_features=["position", "original"],
                surrounding_features=["original"],
            ),
        ),
        ("x", "passthrough"),
    ]
)


label = "¡LA a Bangkok 🇹🇭$8,442! (Por $2,170 agrega 6 noches de Hotel)"

[values] = text.transform([label])

for v in values:
    print()
    print(v)
