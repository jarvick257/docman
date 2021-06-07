from collections import namedtuple

import pytest

import docman
from docman.cli.pdf import _run
from testhelpers import with_test_config


def test_pdf_noscans(capfd):
    doc = docman.Document.load({})
    assert doc.scans == []
    assert _run(doc, None) == (None, 1)
    assert capfd.readouterr() == ("No scans!\n", "")


def test_pdf_ok(capfd, with_test_config):
    doc = docman.Document.load({})
    doc.config["INTEGRATION"]["pdf_conversion"] = "echo convert {source_files} {output}"
    doc.scans = ["one", "two"]
    doc, retval = _run(doc, None)
    assert retval == 0
    assert doc.pdf == "/tmp/test_docman/combined.pdf"
    assert capfd.readouterr() == (
        "convert one two /tmp/test_docman/combined.pdf\n"
        "/tmp/test_docman/combined.pdf\n",
        "",
    )


def test_pdf_err_retval(capfd, with_test_config):
    doc = docman.Document.load({})
    doc.config["INTEGRATION"]["pdf_conversion"] = "python3 -c exit(1)"
    doc.scans = ["one", "two"]
    assert _run(doc, None) == (None, 1)
    assert capfd.readouterr() == (
        "python3 -c exit(1) failed with return value 1!\n",
        "",
    )


def test_pdf_err_unknown(capfd, with_test_config):
    doc = docman.Document.load({})
    doc.config["INTEGRATION"]["pdf_conversion"] = "nonexistingcommand some_arg"
    doc.scans = ["one", "two"]
    assert _run(doc, None) == (None, 1)
    assert capfd.readouterr() == (
        "nonexistingcommand doesn't exist!\n",
        "",
    )
