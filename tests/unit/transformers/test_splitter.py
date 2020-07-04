from transformers.splitter import Splitter
import pytest


@pytest.mark.parametrize(
    ["input_sequence", "position", "expected"],
    [
        ([(["t1", "t2"], [0, 1])], 0, [["t1", "t2"]]),
        ([(["t1", "t2"], [0, 1])], 1, [[0, 1]]),
        ([(["t1", "t2"], [0, 1]), (["k1", "k2"], [2, 3])], 1, [[0, 1], [2, 3]]),
    ],
)
def test_splitter_position(input_sequence, position, expected):
    splitter = Splitter(position)

    actual = splitter.transform(input_sequence)

    assert actual == expected
