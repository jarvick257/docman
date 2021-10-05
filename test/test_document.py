import pdb
import os
import json
import datetime as dt

import pytest
import docman

from testhelpers import with_test_config

test_meta = dict(
    mode="replace",
    _id="some_id",
    input_files=[1, 2, 3],
    tags=[4, 5, 6],
    ocr="some ocr",
    pdf="some pdf",
    date=str(dt.date.today()),
    title="some title",
)


def test_document_load_clean(with_test_config):
    doc = docman.Document.load()
    assert doc._id == None
    assert doc.tags == []
    assert doc.ocr == None
    assert doc.pdf == None
    assert doc.title == None
    assert dt.datetime.now() - doc.date < dt.timedelta(seconds=0.2)
    assert doc.mode == "add"
    assert doc.wd == "/tmp/test_docman"
    assert doc.path == os.path.join(doc.wd, "meta.json")
    assert not doc.is_wip()
    assert doc.to_dict() == dict(
        mode="add",
        _id=None,
        input_files=[],
        tags=[],
        ocr=None,
        pdf=None,
        date=str(doc.date.date()),
        title=None,
    )


def test_document_load_from_dict(with_test_config):
    doc = docman.Document.load(test_meta)
    assert doc.to_dict() == test_meta


def test_document_load_from_file(with_test_config):
    os.mkdir("/tmp/test_docman")
    with open("/tmp/test_docman/meta.json", "w") as fp:
        json.dump(test_meta, fp)
    doc = docman.Document.load()
    assert doc.to_dict() == test_meta


def test_document_save(with_test_config):
    doc = docman.Document.load(test_meta)
    assert not os.path.isfile(doc.path)
    doc.save()
    assert os.path.isfile(doc.path)
    with open(doc.path, "r") as fp:
        meta = json.load(fp)
    assert test_meta == meta


def test_document_is_wip(with_test_config):
    doc = docman.Document.load()
    assert not doc.is_wip()
    doc.tags.append(1)
    assert doc.is_wip()
    doc.tags = []
    doc.ocr = "some ocr"
    assert doc.is_wip()
    doc.ocr = None
    doc.pdf = "some pdf"
    assert doc.is_wip()
    doc.pdf = None
    doc.title = "some title"
    assert doc.is_wip()
    doc.title = None
    assert not doc.is_wip()
