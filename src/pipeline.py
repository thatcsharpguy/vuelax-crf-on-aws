import sklearn_crfsuite
from sklearn.pipeline import Pipeline

from transformers import (
    AugmentTokens,
    POSTagger,
    TextTransform,
    TokenLength,
    TokenListLength,
    Splitter,
    Tokeniser,
    FeaturiseCRF,
)
from transformers.splitter import TupleJoin
from transformers.utils import is_punctuation, is_numeric

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
        ("pos_tags", POSTagger()),
        ("prev_next_pos", previous_next_pos),
        ("x", "passthrough"),
    ]
)
joint_token_features = TupleJoin(
    [
        ("current_uppercase", TextTransform(str.upper)),
        ("current_lowercase", TextTransform(str.lower)),
        ("is_punctuation", TextTransform(is_punctuation)),
        ("is_numeric", TextTransform(is_numeric)),
        ("token_lengths", TokenLength()),
        ("sentence_length", TokenListLength()),
        ("pos_tags", POSTagger()),
        ("pos", pos_pipeline),
    ],
    unpack=["pos"],
)
all_features = Pipeline(
    [
        ("select_tokens", Splitter(0)),
        ("other_features", joint_token_features),
        ("x", "passthrough"),
    ]
)
joint_all_features = TupleJoin(
    [("positions", Splitter(1)), ("tokens", Splitter(0)), ("other", all_features)],
    unpack=["other"],
)
full_pipeline = Pipeline(
    [
        ("tokeniser", Tokeniser(return_flags=True)),
        ("features", joint_all_features),
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
    ]
)
