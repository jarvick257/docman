import json
import requests

import pytest

import docman
from docman.cli.push import _run
from testhelpers import with_test_config, RequestsMock


def test_push_incomplete(with_test_config):
    doc = docman.Document.load({})
    doc.is_complete = lambda: False
    assert _run(doc, None) == (None, 1)


def test_push_add_replace(with_test_config):
    with open("/tmp/test_docman.pdf", "w") as fp:
        fp.write("testpdf")
    with open("/tmp/test_scan_one.jpg", "w") as fp:
        fp.write("testscanone")
    with open("/tmp/test_scan_two.jpg", "w") as fp:
        fp.write("testscantwo")

    for exception in [True, False]:
        for mode in ["add", "replace"]:
            doc = docman.Document.load({})
            doc.mode = mode
            doc._id = "some_id"
            doc.pdf = "/tmp/test_docman.pdf"
            doc.scans = ["/tmp/test_scan_one.jpg", "/tmp/test_scan_two.jpg"]
            doc.tags = ["alpha", "beta"]
            doc.title = "title"
            doc.date = "date"
            doc.ocr = "ocr"
            mock = RequestsMock()
            requests.post = mock.post
            if exception:
                mock.set_post_response("{}", requests.exceptions.ConnectionError)
            else:
                mock.set_post_response("OK", 201)
            doc, retval = _run(doc, None)
            assert mock.last_post_rq is not (None, None, None)
            assert mock.last_post_rq[0] == f"http://localhost:8123/{mode}"
            assert mock.last_post_rq[1] is None
            assert len(mock.last_post_rq[2]) == 4
            assert mock.last_post_rq[2][0][0] == "post"
            assert mock.last_post_rq[2][1][0] == "pdf"
            assert mock.last_post_rq[2][2][0] == "scan"
            assert mock.last_post_rq[2][3][0] == "scan"
            # in replace mode, _id is sent in post
            assert ("_id" in mock.last_post_rq[2][0][1]) == (mode == "replace")
            if exception:
                assert retval == 1
                assert doc is None
            else:
                assert retval == 0
                assert not doc.is_wip()


def test_push_update(with_test_config):
    for exception in [True, False]:
        doc = docman.Document.load({})
        doc.mode = "update"
        doc._id = "some_id"
        doc.tags = ["alpha", "beta"]
        doc.title = "title"
        doc.date = "date"
        doc.ocr = "ocr"
        mock = RequestsMock()
        requests.post = mock.post
        if exception:
            mock.set_post_response("{}", requests.exceptions.ConnectionError)
        else:
            mock.set_post_response("OK", 201)
        doc, retval = _run(doc, None)
        assert mock.last_post_rq is not (None, None, None)
        assert mock.last_post_rq[0] == "http://localhost:8123/update"
        assert mock.last_post_rq[2] is None
        post = mock.last_post_rq[1]
        assert isinstance(post, dict)
        assert "_id" in post
        if exception:
            assert retval == 1
            assert doc is None
        else:
            assert retval == 0
            assert doc.is_wip() == False


def test_push_retval(with_test_config):
    doc = docman.Document.load({})
    doc.mode = "update"
    doc._id = "some_id"
    doc.tags = ["alpha", "beta"]
    doc.title = "title"
    doc.date = "date"
    doc.ocr = "ocr"
    mock = RequestsMock()
    requests.post = mock.post
    mock.set_post_response("OK", 200)
    assert _run(doc, None) == (None, 1)
