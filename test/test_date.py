from collections import namedtuple
from datetime import date

import pytest

import docman
from docman.cli.date import _run


def args(**kwargs):
    fake_args = namedtuple("args", ("date"))
    return fake_args(kwargs["date"])  # required


def test_date_simple(capfd):
    doc = docman.Document()
    assert doc.date is None
    doc, retval = _run(doc, args(date=["2021-01-01"]))
    assert retval == 0
    assert doc.date == date(2021, 1, 1)
    assert capfd.readouterr() == ("2021-01-01\n", "")


def test_date_multiple(capfd):
    doc = docman.Document()
    assert doc.date is None
    doc, retval = _run(doc, args(date=["2021", "01", "01"]))
    assert retval == 0
    assert doc.date == date(2021, 1, 1)
    assert capfd.readouterr() == ("2021-01-01\n", "")


def test_date_invalid(capfd):
    doc = docman.Document()
    assert doc.date is None
    doc, retval = _run(doc, args(date=["2021", "13", "01"]))
    assert retval == 1
    assert doc is None
    assert capfd.readouterr() == ("Date must be in YYYY-MM-DD format.\n", "")
