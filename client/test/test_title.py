from collections import namedtuple

import pytest

import docman
from docman.cli.title import _run


def args(**kwargs):
    fake_args = namedtuple("args", ("clear", "title"))
    return fake_args(
        kwargs.get("clear", False),
        kwargs.get("title", []),
    )


def test_title_clear(capfd):
    doc = docman.Document()
    doc.title = "some title"
    doc = _run(doc, args(clear=True))
    assert doc.title is None
    assert capfd.readouterr() == ("\n", "")


def test_title_set(capfd):
    doc = docman.Document()
    assert doc.title is None
    doc = _run(doc, args(title=["Single Arg Title"]))
    assert doc.title == "Single_Arg_Title"
    assert capfd.readouterr() == ("Single_Arg_Title\n", "")
    doc = _run(doc, args(title=["Multi", "Arg Title"]))
    assert doc.title == "Multi_Arg_Title"
    assert capfd.readouterr() == ("Multi_Arg_Title\n", "")


def test_title_noarg(capfd):
    doc = docman.Document()
    doc.title = "some_title"
    doc = _run(doc, args())
    assert doc.title == "some_title"
    assert capfd.readouterr() == ("some_title\n", "")
