import json
import requests
import urllib.request
from collections import namedtuple

import pytest

import docman
from docman.cli.pull import _run
from testhelpers import with_test_config, RequestsMock


def args(**kwargs):
    fake_args = namedtuple("args", ("id", "scans", "all", "output"))
    return fake_args(
        kwargs["id"],
        kwargs.get("scans", False),
        kwargs.get("all", False),
        kwargs.get("output", "."),
    )


def test_pull_pdf(with_test_config):
    doc = docman.Document.load({})
    mock = RequestsMock()
    requests.get = mock.get
    urllib.request.urlretrieve = mock.urlretrieve
    response = dict(some_id=dict(_id="some_id", pdf="some_pdf", scans=["one", "two"]))
    mock.set_get_response(json.dumps(response), 200)
    assert _run(doc, args(id="some_id")) == (None, 0)
    assert mock.last_get_rq == ("http://localhost:8123/query", dict(id="some_id"), None)
    assert len(mock.urlretrieve_requests) == 1
    assert mock.urlretrieve_requests[0] == (
        "http://localhost:8123/pdf/some_pdf",
        "./some_pdf",
    )


def test_pull_scans(with_test_config):
    doc = docman.Document.load({})
    mock = RequestsMock()
    requests.get = mock.get
    urllib.request.urlretrieve = mock.urlretrieve
    response = dict(some_id=dict(_id="some_id", pdf="some_pdf", scans=["one", "two"]))
    mock.set_get_response(json.dumps(response), 200)
    assert _run(doc, args(id="some_id", scans=True, output="some/output")) == (None, 0)
    assert mock.last_get_rq == ("http://localhost:8123/query", dict(id="some_id"), None)
    assert len(mock.urlretrieve_requests) == 2
    assert mock.urlretrieve_requests[0] == (
        "http://localhost:8123/scan/one",
        "some/output/one",
    )
    assert mock.urlretrieve_requests[1] == (
        "http://localhost:8123/scan/two",
        "some/output/two",
    )


def test_pull_all(with_test_config):
    doc = docman.Document.load({})
    mock = RequestsMock()
    requests.get = mock.get
    urllib.request.urlretrieve = mock.urlretrieve
    response = dict(some_id=dict(_id="some_id", pdf="some_pdf", scans=["one", "two"]))
    mock.set_get_response(json.dumps(response), 200)
    assert _run(doc, args(id="some_id", all=True, output="some/output")) == (None, 0)
    assert mock.last_get_rq == ("http://localhost:8123/query", dict(id="some_id"), None)
    assert len(mock.urlretrieve_requests) == 3
    assert mock.urlretrieve_requests[0] == (
        "http://localhost:8123/scan/one",
        "some/output/one",
    )
    assert mock.urlretrieve_requests[1] == (
        "http://localhost:8123/scan/two",
        "some/output/two",
    )
    assert mock.urlretrieve_requests[2] == (
        "http://localhost:8123/pdf/some_pdf",
        "some/output/some_pdf",
    )


def test_pull_wrong_retval(with_test_config):
    doc = docman.Document.load({})
    mock = RequestsMock()
    requests.get = mock.get
    urllib.request.urlretrieve = mock.urlretrieve
    response = dict(some_id=dict(_id="some_id", pdf="some_pdf", scans=["one", "two"]))
    mock.set_get_response(json.dumps(response), 201)
    assert _run(doc, args(id="some_id", all=True, output="some/output")) == (None, 1)
    assert mock.last_get_rq == ("http://localhost:8123/query", dict(id="some_id"), None)
    assert len(mock.urlretrieve_requests) == 0


def test_pull_exception(with_test_config):
    doc = docman.Document.load({})
    mock = RequestsMock()
    requests.get = mock.get
    urllib.request.urlretrieve = mock.urlretrieve
    mock.set_get_response("{}", requests.exceptions.ConnectionError)
    assert _run(doc, args(id="some_id", all=True, output="some/output")) == (None, 1)
    assert mock.last_get_rq == ("http://localhost:8123/query", dict(id="some_id"), None)
    assert len(mock.urlretrieve_requests) == 0
