from collections import namedtuple

import pytest

import docman
from docman.cli.tag import _run


def args(**kwargs):
    fake_args = namedtuple("args", ("clear", "remove", "add", "tags"))
    return fake_args(
        kwargs.get("clear", False),
        kwargs.get("remove", []),
        kwargs.get("add", []),
        kwargs.get("tags", []),
    )


def test_tag_add(capfd):
    doc = docman.Document.load({})
    doc.tags = ["alpha", "beta"]
    # add single
    doc, retval = _run(doc, args(add=["gamma"]))
    assert retval == 0
    assert doc.tags == ["alpha", "beta", "gamma"]
    assert capfd.readouterr() == ("alpha beta gamma\n", "")
    # add multiple
    doc, retval = _run(doc, args(add=["one", "two"]))
    assert retval == 0
    assert doc.tags == ["alpha", "beta", "gamma", "one", "two"]
    assert capfd.readouterr() == ("alpha beta gamma one two\n", "")
    # Existing tags are ignored
    doc, retval = _run(doc, args(add=["one", "two"]))
    assert retval == 0
    assert doc.tags == ["alpha", "beta", "gamma", "one", "two"]
    assert capfd.readouterr() == ("alpha beta gamma one two\n", "")
    # Add without --add flag (positional)
    doc, retval = _run(doc, args(tags=["aa", "bb"]))
    assert retval == 0
    assert doc.tags == ["aa", "alpha", "bb", "beta", "gamma", "one", "two"]
    assert capfd.readouterr() == ("aa alpha bb beta gamma one two\n", "")


def test_tag_remove(capfd):
    doc = docman.Document()
    doc.tags = ["alpha", "beta"]
    doc, retval = _run(doc, args(remove=["beta", "gamma"]))
    assert retval == 0
    assert doc.tags == ["alpha"]
    assert capfd.readouterr() == ("alpha\n", "")


def test_tag_clear(capfd):
    doc = docman.Document()
    doc.tags = ["alpha", "beta"]
    doc, retval = _run(doc, args(clear=True))
    assert retval == 0
    assert doc.tags == []
    assert capfd.readouterr() == ("\n", "")


def test_tag_combination(capfd):
    doc = docman.Document()
    doc.tags = ["alpha", "beta"]
    doc, retval = _run(doc, args(clear=True, tags=["one", "two"]))
    assert retval == 0
    assert doc.tags == ["one", "two"]
    assert capfd.readouterr() == ("one two\n", "")
