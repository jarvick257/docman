from collections import namedtuple

import pytest

import docman
from docman.cli.mode import _run


def args(**kwargs):
    fake_args = namedtuple("args", ("mode", "id"))
    assert kwargs["mode"] in ["add", "update", "replace"]
    return fake_args(kwargs["mode"], kwargs.get("id", None))  # required


def test_mode_add(capfd):
    # without id
    doc = docman.Document.load({})
    doc.mode = None
    doc, retval = _run(doc, args(mode="add"))
    assert retval == 0
    assert doc.mode == "add"
    assert capfd.readouterr() == ("add\n", "")
    # with id
    doc.mode = None
    doc, retval = _run(doc, args(mode="add", id="some_id"))
    assert retval == 0
    assert doc.mode == "add"
    assert doc._id == "some_id"
    out, err = capfd.readouterr()
    out = out.split("\n")
    assert err == ""
    assert out[0] == (
        "Warning: Adding a document for a given ID is not supported. "
        "The specified id will be ignored."
    )
    assert out[1] == "add"


def test_mode_replace(capfd):
    # without id
    doc = docman.Document.load({})
    doc.mode = None
    doc, retval = _run(doc, args(mode="replace"))
    assert retval == 1
    assert doc is None
    assert capfd.readouterr() == (
        "Error: When choosing a mode other than 'add', an existing document id is required!\n",
        "",
    )
    # with new id
    doc = docman.Document.load({})
    doc._id = "old id"
    doc.mode = None
    doc, retval = _run(doc, args(mode="replace", id="some_id"))
    assert retval == 0
    assert doc.mode == "replace"
    assert doc._id == "some_id"
    capfd.readouterr() == ("replace\n", "")
    # existing id
    doc = docman.Document.load({})
    doc._id = "old id"
    doc.mode = None
    doc, retval = _run(doc, args(mode="replace"))
    assert retval == 0
    assert doc.mode == "replace"
    assert doc._id == "old id"
    capfd.readouterr() == ("replace\n", "")


def test_mode_update(capfd):
    # without id
    doc = docman.Document.load({})
    doc.mode = None
    doc, retval = _run(doc, args(mode="update"))
    assert retval == 1
    assert doc is None
    assert capfd.readouterr() == (
        "Error: When choosing a mode other than 'add', an existing document id is required!\n",
        "",
    )
    # with new id
    doc = docman.Document.load({})
    doc._id = "old id"
    doc.mode = None
    doc, retval = _run(doc, args(mode="update", id="some_id"))
    assert retval == 0
    assert doc.mode == "update"
    assert doc._id == "some_id"
    capfd.readouterr() == ("update\n", "")
    # existing id
    doc = docman.Document.load({})
    doc._id = "old id"
    doc.mode = None
    doc, retval = _run(doc, args(mode="update"))
    assert retval == 0
    assert doc.mode == "update"
    assert doc._id == "old id"
    capfd.readouterr() == ("update\n", "")
