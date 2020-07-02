import pytest
from sklearn.base import BaseEstimator, TransformerMixin

from transformers.lengths import TokenLength, TokenListLength


@pytest.mark.parametrize(
    ["token_list", "expected_lengths"],
    [([["", "a", "ab", "abc"]], [[0, 1, 2, 3]]), ([["1234"]], [[4]]), ([], [])],
)
def test_token_length(token_list, expected_lengths):
    transformer = TokenLength()

    actual_lengths = transformer.transform(token_list)

    assert actual_lengths == expected_lengths


@pytest.mark.parametrize(
    ["token_list", "expected_lengths"],
    [([["a", "ab", "abc"]], [[3, 3, 3]]), ([["a"]], [[1]]), ([], [])],
)
def test_token_list_length(token_list, expected_lengths):
    transformer = TokenListLength()

    actual_lengths = transformer.transform(token_list)

    assert actual_lengths == expected_lengths
