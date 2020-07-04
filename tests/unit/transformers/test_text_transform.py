from transformers.text_transform import TextTransform
import pytest


@pytest.mark.parametrize(
    ["tokens", "expected"],
    [(["a", "b", "C"], ["A", "B", "C"]), (["A", "B", "C"], ["A", "B", "C"]),],
)
def test_transform_uppercase(tokens, expected):
    text_transform = TextTransform(str.upper)

    actual = text_transform.transform([tokens])

    assert actual == [expected]
