from unittest.mock import patch, MagicMock

from transformers.pos_tagger import POSTagger
import pytest


def test_tagger_init():
    path = "/a/path"

    jar_file_expected = "/a/path/stanford-postagger.jar"
    tagger_file_expected = "/a/path/spanish.tagger"

    with patch("transformers.pos_tagger.StanfordPOSTagger") as pos_tagger_patch:
        tagger = POSTagger(models_path=path)

        pos_tagger_patch.assert_called_once_with(
            tagger_file_expected, jar_file_expected
        )
        assert tagger.tagger is not None


@pytest.fixture
def patched_tagger():
    with patch("transformers.pos_tagger.StanfordPOSTagger"):
        tagger = POSTagger("dummy")
        tagger.tagger = MagicMock()

        yield tagger


def test_tagger_tag(patched_tagger):
    token_list = ["a", "b"]
    expected = ["pos_tag_1", "pos_tag_2"]

    patched_tagger.tagger.tag = MagicMock(
        return_value=[("a", "pos_tag_1"), ("b", "pos_tag_2")]
    )

    actual = patched_tagger.tag(token_list)
    assert actual == expected
    patched_tagger.tagger.tag.assert_called_once_with(token_list)


@pytest.mark.parametrize("calls", [0, 1, 10])
def test_tagger_transform(patched_tagger, calls):

    sentences = [[f"a {idx}", f"b {idx}"] for idx in range(calls)]

    with patch.object(patched_tagger, "tag") as tag_mocked:
        result = patched_tagger.transform(sentences)

        assert len(result) == calls
        assert tag_mocked.call_count == calls
