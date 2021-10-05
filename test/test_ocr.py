from collections import namedtuple

import pytest
import pytesseract
from queue import Queue


import docman
from docman.cli.ocr import _run, _ocr_worker
from testhelpers import with_test_config


def args(**kwargs):
    fake_args = namedtuple("args", ("lang", "max_jobs"))
    return fake_args(kwargs.get("lang", None), int(kwargs.get("max_jobs", 4)))


def image_to_string_mock(file, lang=None):
    return f"file: {file}, lang: {lang}\n"


def test_ocr_worker(with_test_config):
    job_q = Queue()
    result_q = Queue()
    pytesseract.image_to_string = image_to_string_mock

    job_q.put(("one", "en"))
    job_q.put(("two", "two"))
    job_q.put(("three", "e\nn"))
    job_q.put(("two", "de"))
    job_q.put((None, None))
    _ocr_worker(job_q, result_q)
    assert result_q.get() == ["en", "file", "lang", "one"]
    assert result_q.get() == ["file", "lang", "two"]
    assert result_q.get() == ["e", "file", "lang", "n", "three"]
    assert result_q.get() == ["de", "file", "lang", "two"]
    assert result_q.empty()


def test_ocr_main(with_test_config):
    pytesseract.image_to_string = image_to_string_mock
    doc = docman.Document.load({})
    doc.scans = ["one", "two", "three"]
    doc, retval = _run(doc, args())
    assert retval == 0
    assert doc.ocr == "eng file lang one three two"
