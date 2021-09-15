from collections import namedtuple

import pytest

import docman
from docman.cli.pdf import _run
from testhelpers import with_test_config


def test_pdf_noinputfiles(capfd):
    doc = docman.Document.load({})
    assert doc.input_files == []
    assert _run(doc, None) == (None, 1)
    assert capfd.readouterr() == ("No input files!\n", "")
