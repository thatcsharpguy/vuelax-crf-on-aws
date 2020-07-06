import os
from unittest.mock import patch

import pytest

from tagger import Tagger


@pytest.fixture
def patched_tagger():
    with patch.object(Tagger, "__init__", lambda *args, **kwargs: None):
        yield Tagger("path")


@pytest.mark.parametrize(
    ["tokens", "labels", "expected"],
    [
        (
            ["Mexico", "Santiago", "123"],
            ["o", "d", "p"],
            {"destination": "Santiago", "origin": "Mexico", "price": "123"},
        ),
        (
            ["Mexico", "Santiago", ",", "Chile", "123"],
            ["o", "d", "d", "d", "p"],
            {"destination": "Santiago , Chile", "origin": "Mexico", "price": "123"},
        ),
        (
            ["Santiago", ",", "Chile", "123"],
            ["d", "d", "d", "p"],
            {"destination": "Santiago , Chile", "price": "123"},
        ),
    ],
)
def test_merge_by_label(patched_tagger, tokens, labels, expected):
    actual = patched_tagger._merge_by_label(tokens, labels)
    assert actual == expected
