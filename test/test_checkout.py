from collections import namedtuple
import json
import requests
import urllib.request
import pytest

import docman
from docman.cli.checkout import _run
from testhelpers import RequestsMock, with_test_config


def args(**kwargs):
    fake_args = namedtuple("args", ("id", "update"))
    return fake_args(
        kwargs["id"],  # required
        kwargs.get("update", False),
    )


def test_checkout_update(capfd):
    doc = docman.Document.load({})
    mock = RequestsMock()
    requests.get = mock.get
    response = dict(some_id=dict(_id="some_id", date="2021-01-01", tags=[1, 2, 3]))
    mock.set_get_response(json.dumps(response), 200)
    doc, retval = _run(doc, args(id="some_id", update=True))
    assert doc._id == "some_id"
    assert doc.mode == "update"
    assert doc.date == "2021-01-01"
    assert doc.tags == [1, 2, 3]
    assert capfd.readouterr() == ("some_id\n", "")


def test_checkout_iswip(capfd):
    doc = docman.Document.load({})
    doc.input_files = [1]
    assert _run(doc, args(id="some_id", update=True)) == (None, 1)


def test_checkout_wrongid(capfd):
    # retval
    doc = docman.Document.load({})
    mock = RequestsMock()
    requests.get = mock.get
    mock.set_get_response("{}", 404)
    assert _run(doc, args(id="some_id", update=True)) == (None, 1)
    assert capfd.readouterr() == ("Didn't find any document for id some_id\n", "")
    # empty response
    doc = docman.Document.load({})
    mock = RequestsMock()
    requests.get = mock.get
    mock.set_get_response("{}", 200)
    assert _run(doc, args(id="some_id", update=True)) == (None, 1)
    assert capfd.readouterr() == ("Didn't find any document for id some_id\n", "")


def test_checkout_exception(capfd, with_test_config):
    # empty response
    doc = docman.Document.load({})
    mock = RequestsMock()
    requests.get = mock.get
    mock.set_get_response("{}", requests.exceptions.ConnectionError)
    assert _run(doc, args(id="some_id", update=True)) == (None, 1)
    assert capfd.readouterr() == (
        "Failed to connect to http://localhost:8123/query\n",
        "",
    )


def test_checkout_full(capfd, with_test_config):
    # empty response
    doc = docman.Document.load({})
    mock = RequestsMock()
    requests.get = mock.get
    urllib.request.urlretrieve = mock.urlretrieve
    response = dict(
        some_id=dict(
            _id="some_id", pdf="some_pdf", input_files=["one", "two"], tags=[1, 2]
        )
    )
    mock.set_get_response(json.dumps(response), 200)
    doc, retval = _run(doc, args(id="some_id"))
    assert retval == 0
    out, err = capfd.readouterr()
    assert err == ""
    assert (
        out == "\rDownloading 1/3\rDownloading 2/3\rDownloading 3/3\rsome_id         \n"
    )
    assert mock.urlretrieve_requests[0] == (
        "http://localhost:8123/pdf/some_pdf",
        "/tmp/test_docman/combined.pdf",
    )
    assert mock.urlretrieve_requests[1] == (
        "http://localhost:8123/scan/one",
        "/tmp/test_docman/one",
    )
    assert mock.urlretrieve_requests[2] == (
        "http://localhost:8123/scan/two",
        "/tmp/test_docman/two",
    )
    assert doc._id == "some_id"
    assert doc.tags == [1, 2]
    assert doc.input_files == ["/tmp/test_docman/one", "/tmp/test_docman/two"]
    assert doc.pdf == "/tmp/test_docman/combined.pdf"
    assert doc.mode == "replace"
