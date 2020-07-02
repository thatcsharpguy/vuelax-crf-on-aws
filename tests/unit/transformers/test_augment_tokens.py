from transformers.augment_tokens import AugmentTokens
import pytest


@pytest.mark.parametrize(
    ["original_tokens", "return_previous", "expected"],
    [
        (["europa", "asia", "america"], "next", ["asia", "america", "</p>"]),
        (["europa", "asia", "america"], "prev", ["<p>", "europa", "asia"]),
        (["europa"], "prev", ["<p>"]),
        ([], "prev", []),
    ],
)
def test_augment_tokens_slice_sequence(original_tokens, return_previous, expected):
    start_token = "<p>"
    end_token = "</p>"

    augment_tokens = AugmentTokens(
        start_tokens=start_token, end_tokens=end_token, which=return_previous
    )

    actual = augment_tokens.slice_sequence(original_tokens)

    assert actual == expected
