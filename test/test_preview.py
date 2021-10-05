from collections import namedtuple
import os

import pytest

import docman
from docman.cli.preview import _run
from testhelpers import with_test_config


def args(**kwargs):
    fake_args = namedtuple("args", ("scans", "pdf"))
    return fake_args(kwargs.get("scans", False), kwargs.get("pdf", False))


last_system_call = []


def os_system_mock(cmd):
    global last_system_call
    last_system_call.append(cmd)


def test_preview_auto(with_test_config):
    global last_system_call
    f = os.system
    os.system = os_system_mock
    # scans and pdf -> show pdf
    doc = docman.Document.load({})
    last_system_call = []
    doc.pdf = "some_pdf"
    doc.scans = ["one", "two"]
    assert _run(doc, args()) == (None, 0)
    assert last_system_call == ["test_pdf_prev some_pdf"]
    # only pdf -> show pdf
    last_system_call = []
    doc.pdf = "some_pdf"
    doc.scans = []
    assert _run(doc, args()) == (None, 0)
    assert last_system_call == ["test_pdf_prev some_pdf"]
    # only scans -> show scans
    last_system_call = []
    doc.pdf = None
    doc.scans = ["one", "two"]
    assert _run(doc, args()) == (None, 0)
    assert last_system_call == ["test_img_prev one two"]
    # nothing -> show nothing
    last_system_call = []
    doc.pdf = None
    doc.scans = []
    assert _run(doc, args()) == (None, 0)
    assert last_system_call == []
    os.system = f


def test_preview_pdf(with_test_config):
    global last_system_call
    f = os.system
    os.system = os_system_mock
    # scans and pdf -> show pdf
    doc = docman.Document.load({})
    last_system_call = []
    doc.pdf = "some_pdf"
    doc.scans = ["one", "two"]
    assert _run(doc, args(pdf=True)) == (None, 0)
    assert last_system_call == ["test_pdf_prev some_pdf"]
    # only pdf -> show pdf
    last_system_call = []
    doc.pdf = "some_pdf"
    doc.scans = []
    assert _run(doc, args(pdf=True)) == (None, 0)
    assert last_system_call == ["test_pdf_prev some_pdf"]
    # only scans -> show nothing
    last_system_call = []
    doc.pdf = None
    doc.scans = ["one", "two"]
    assert _run(doc, args(pdf=True)) == (None, 0)
    assert last_system_call == []
    # nothing -> show nothing
    last_system_call = []
    doc.pdf = None
    doc.scans = []
    assert _run(doc, args(pdf=True)) == (None, 0)
    assert last_system_call == []
    os.system = f


def test_preview_scans(with_test_config):
    global last_system_call
    f = os.system
    os.system = os_system_mock
    # scans and pdf -> show scans
    doc = docman.Document.load({})
    last_system_call = []
    doc.pdf = "some_pdf"
    doc.scans = ["one", "two"]
    assert _run(doc, args(scans=True)) == (None, 0)
    assert last_system_call == ["test_img_prev one two"]
    # only pdf -> show nothing
    last_system_call = []
    doc.pdf = "some_pdf"
    doc.scans = []
    assert _run(doc, args(scans=True)) == (None, 0)
    assert last_system_call == []
    # only scans -> show scans
    last_system_call = []
    doc.pdf = None
    doc.scans = ["one", "two"]
    assert _run(doc, args(scans=True)) == (None, 0)
    assert last_system_call == ["test_img_prev one two"]
    # nothing -> show nothing
    last_system_call = []
    doc.pdf = None
    doc.scans = []
    assert _run(doc, args(scans=True)) == (None, 0)
    assert last_system_call == []
    os.system = f


def test_preview_all(with_test_config):
    global last_system_call
    f = os.system
    os.system = os_system_mock
    # scans and pdf -> show all
    doc = docman.Document.load({})
    last_system_call = []
    doc.pdf = "some_pdf"
    doc.scans = ["one", "two"]
    assert _run(doc, args(scans=True, pdf=True)) == (None, 0)
    assert last_system_call == ["test_pdf_prev some_pdf", "test_img_prev one two"]
    # only pdf -> show pdf
    last_system_call = []
    doc.pdf = "some_pdf"
    doc.scans = []
    assert _run(doc, args(scans=True, pdf=True)) == (None, 0)
    assert last_system_call == ["test_pdf_prev some_pdf"]
    # only scans -> show scans
    last_system_call = []
    doc.pdf = None
    doc.scans = ["one", "two"]
    assert _run(doc, args(scans=True, pdf=True)) == (None, 0)
    assert last_system_call == ["test_img_prev one two"]
    # nothing -> show nothing
    last_system_call = []
    doc.pdf = None
    doc.scans = []
    assert _run(doc, args(scans=True)) == (None, 0)
    assert last_system_call == []
    os.system = f
