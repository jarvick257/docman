import os
from collections import namedtuple

import pytest

import docman
from docman.cli.reset import _run
from testhelpers import with_test_config


def args(**kwargs):
    fake_args = namedtuple("args", ("hard"))
    return fake_args(
        kwargs.get("hard", False),
    )


def test_reset(with_test_config):
    # create 'is' state for document
    doc = docman.Document.load({})
    doc.input_files = ["one", "two", "three"]
    doc.tags = ["alpha", "beta"]
    doc.pdf = "some pdf"
    doc.ocr = "some ocr"

    # create "actual" input files
    os.mkdir(doc.wd)
    for f in ["four.jpg", "five.jpg", "six.png"]:
        with open(os.path.join(doc.wd, f), "w") as fp:
            fp.write("")

    # soft reset will reset all meta data and check for input files
    doc, retval = _run(doc, args(hard=False))
    assert retval == 0
    assert doc.input_files == sorted(
        ["/tmp/test_docman/five.jpg", "/tmp/test_docman/four.jpg"]
    )
    assert doc.tags == []
    assert doc.pdf is None
    assert doc.ocr is None

    # hard reset will also delete input files
    doc, retval = _run(doc, args(hard=True))
    assert retval == 0
    assert doc.input_files == []
