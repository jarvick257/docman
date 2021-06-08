import json
from collections import namedtuple

import pytest

import docman
from docman.cli.status import _run


def args(**kwargs):
    fake_args = namedtuple("args", ("json", "full_ocr"))
    return fake_args(
        kwargs.get("json", False),
        kwargs.get("full_ocr", False),
    )


def get_default_doc():
    doc = docman.Document()
    doc.tags = ["alpha", "omega"]
    doc.title = "some_title"
    doc.ocr = "this is some ocr"
    doc.scans = [1, 2, 3]
    doc.date = "some date"
    doc.pdf = "some pdf"
    doc.mode = "add"
    doc._id = "some id"
    return doc


def test_status_noarg(capfd):
    doc = get_default_doc()
    assert _run(doc, args()) == (None, 0)
    out, err = capfd.readouterr()
    assert err == ""
    out = out.split("\n")
    assert out[0] == "Mode:  add"
    assert out[1] == "Title: some_title"
    assert out[2] == "Date:  some date"
    assert out[3] == "Tags:  alpha omega"
    assert out[4] == "Scans: 3"
    assert out[5] == "Ocr:   4 words"
    assert out[6] == "Pdf:   Yes"


def test_status_mode(capfd):
    # Add
    doc = get_default_doc()
    doc._id = "some id"
    doc.mode = "add"
    assert _run(doc, args()) == (None, 0)
    capfd.readouterr()[0].split("\n")[0] == "Mode:  add"
    # Replace
    doc.mode = "replace"
    assert _run(doc, args()) == (None, 0)
    capfd.readouterr()[0].split("\n")[0] == "Mode:  replace some id"
    # Replace
    doc.mode = "edit"
    assert _run(doc, args()) == (None, 0)
    capfd.readouterr()[0].split("\n")[0] == "Mode:  edit some id"


def test_status_ocr(capfd):
    doc = get_default_doc()
    assert _run(doc, args(full_ocr=True)) == (None, 0)
    assert capfd.readouterr()[0].split("\n")[5] == "Ocr:   this is some ocr"

    doc = get_default_doc()
    doc.ocr = None
    assert _run(doc, args()) == (None, 0)
    assert capfd.readouterr()[0].split("\n")[5] == "Ocr:   0 words"

    doc = get_default_doc()
    doc.ocr = None
    assert _run(doc, args(full_ocr=True)) == (None, 0)
    assert capfd.readouterr()[0].split("\n")[5] == "Ocr:   None"


def test_status_json(capfd):
    doc = get_default_doc()
    assert _run(doc, args(json=True)) == (None, 0)
    out, err = capfd.readouterr()
    d = dict(
        tags=["alpha", "omega"],
        title="some_title",
        ocr="4 words",
        scans=[1, 2, 3],
        date="some date",
        pdf="some pdf",
        mode="add",
        _id="some id",
    )
    assert err == ""
    assert json.loads(out) == d

    doc = get_default_doc()
    assert _run(doc, args(json=True, full_ocr=True)) == (None, 0)
    out, err = capfd.readouterr()
    d["ocr"] = "this is some ocr"
    assert err == ""
    assert json.loads(out) == d