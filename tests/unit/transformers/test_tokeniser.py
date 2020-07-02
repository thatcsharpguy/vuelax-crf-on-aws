from unittest.mock import patch, MagicMock

from transformers.pos_tagger import POSTagger
from transformers.tokeniser import Tokeniser
import pytest


@pytest.mark.parametrize(
    ["sentence", "return_flags", "expected_output"],
    [
        (
            "¡MTY a Cusco, Perú 🇵🇪 $5,257! (Por $1,761 agrega 7 noches de hotel con desayunos)",
            False,
            (
                [
                    "¡",
                    "MTY",
                    "a",
                    "Cusco",
                    ",",
                    "Perú",
                    "$",
                    "5,257",
                    "!",
                    "(",
                    "Por",
                    "$",
                    "1,761",
                    "agrega",
                    "7",
                    "noches",
                    "de",
                    "hotel",
                    "con",
                    "desayunos",
                    ")",
                ],
                [
                    0,
                    1,
                    5,
                    7,
                    12,
                    14,
                    22,
                    23,
                    28,
                    30,
                    31,
                    22,
                    36,
                    42,
                    27,
                    51,
                    58,
                    61,
                    67,
                    71,
                    80,
                ],
            ),
        ),
        (
            "¡MTY a Cusco, Perú 🇵🇪 $5,257! (Por $1,761 agrega 7 noches de hotel con desayunos)",
            True,
            (
                [
                    "¡",
                    "MTY",
                    "a",
                    "Cusco",
                    ",",
                    "Perú",
                    "🇵🇪",
                    "$",
                    "5,257",
                    "!",
                    "(",
                    "Por",
                    "$",
                    "1,761",
                    "agrega",
                    "7",
                    "noches",
                    "de",
                    "hotel",
                    "con",
                    "desayunos",
                    ")",
                ],
                [
                    0,
                    1,
                    5,
                    7,
                    12,
                    14,
                    19,
                    22,
                    23,
                    28,
                    30,
                    31,
                    22,
                    36,
                    42,
                    27,
                    51,
                    58,
                    61,
                    67,
                    71,
                    80,
                ],
            ),
        ),
        (
            "¡MTY a Cusco, Perú $5,257! (Por $1,761 agrega 7 noches de hotel con desayunos)",
            True,
            (
                [
                    "¡",
                    "MTY",
                    "a",
                    "Cusco",
                    ",",
                    "Perú",
                    "$",
                    "5,257",
                    "!",
                    "(",
                    "Por",
                    "$",
                    "1,761",
                    "agrega",
                    "7",
                    "noches",
                    "de",
                    "hotel",
                    "con",
                    "desayunos",
                    ")",
                ],
                [
                    0,
                    1,
                    5,
                    7,
                    12,
                    14,
                    19,
                    20,
                    25,
                    27,
                    28,
                    19,
                    33,
                    39,
                    24,
                    48,
                    55,
                    58,
                    64,
                    68,
                    77,
                ],
            ),
        ),
        (
            "✈️ Aerolíneas y agencias: Avisos de flexibilidad, cambios y más 🙂",
            False,
            (
                [
                    "✈",
                    "️",
                    "Aerolíneas",
                    "y",
                    "agencias",
                    ":",
                    "Avisos",
                    "de",
                    "flexibilidad",
                    ",",
                    "cambios",
                    "y",
                    "más",
                ],
                [0, 1, 3, 14, 16, 24, 26, 33, 36, 48, 50, 14, 60],
            ),
        ),
    ],
)
def test_tokeniser_tokenise(sentence, return_flags, expected_output):
    tokeniser = Tokeniser(return_flags=return_flags)

    actual = tokeniser.tokenise(sentence)
    assert actual == expected_output


@pytest.mark.parametrize("calls", [0, 1, 10])
def test_tokeniser_transform(calls):
    tokeniser = Tokeniser()

    sentences = [f"Sentence [{idx}]" for idx in range(calls)]

    with patch.object(tokeniser, "tokenise") as tokenise_mocked:
        result = tokeniser.transform(sentences)

        assert len(result) == calls
        assert tokenise_mocked.call_count == calls
