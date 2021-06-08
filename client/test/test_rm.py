import json
from collections import namedtuple
import pytest
import requests

import docman
from docman.cli.rm import _run
from testhelpers import RequestsMock, with_test_config, replace_stdin


def args(**kwargs):
    fake_args = namedtuple("args", ("ids", "noconfirm"))
    return fake_args(
        kwargs["ids"],  # required
        kwargs.get("noconfirm", False),
    )


def test_rm_single(capfd, with_test_config):
    doc = docman.Document.load({})
    mock = RequestsMock()
    requests.get = mock.get
    requests.post = mock.post
    # response for id lookup
    mock.set_get_response(json.dumps(dict(some_id=dict(scans=[1, 2, 3]))), 200)
    # response for remove call
    mock.set_post_response("OK", 201)

    with replace_stdin("yes"):
        assert _run(doc, args(ids=["some_id"], noconfirm=False)) == (None, 0)
    assert mock.last_get_rq == (
        "http://localhost:8123/query",
        {"id": "some_id"},
        None,
    )
    assert mock.last_post_rq == (
        "http://localhost:8123/remove",
        {"ids": ["some_id"]},
        None,
    )
    out, err = capfd.readouterr()
    assert err == ""
    out = out.split("\n")
    assert out[0] == "You are about to delete 1 document (3 scans)."
    assert out[1] == (
        "If you wish to continue, please type yes: Successfully removed 1 document"
    )


def test_rm_multiple(capfd, with_test_config):
    doc = docman.Document.load({})
    mock = RequestsMock()
    requests.get = mock.get
    requests.post = mock.post
    # response for id lookup
    mock.set_get_response(json.dumps(dict(one=dict(scans=[1, 2, 3]))), 200)
    mock.set_get_response(json.dumps(dict(two=dict(scans=[1, 2]))), 200)
    # response for remove call
    mock.set_post_response("OK", 201)

    assert _run(doc, args(ids=["one", "one", "two"], noconfirm=True)) == (None, 0)
    assert mock.last_get_rq == (
        "http://localhost:8123/query",
        {"id": "two"},
        None,
    )
    assert mock.last_post_rq == (
        "http://localhost:8123/remove",
        {"ids": ["one", "two"]},
        None,
    )
    out, err = capfd.readouterr()
    assert err == ""
    out = out.split("\n")
    assert out[0] == "You are about to delete 2 documents (5 scans)."
    assert out[1] == "Successfully removed 2 documents"


def test_rm_nothing(capfd, with_test_config):
    doc = docman.Document.load({})
    mock = RequestsMock()
    requests.get = mock.get
    mock.set_get_response("{}", 404)
    assert _run(doc, args(ids=["zero"], noconfirm=True)) == (None, 0)
    out, err = capfd.readouterr()
    assert err == ""
    out = out.split("\n")
    assert out[0] == "Warning: No document found for id zero"
    assert out[1] == "Nothing to delete."


def test_rm_fail(capfd, with_test_config):
    doc = docman.Document.load({})
    mock = RequestsMock()
    requests.get = mock.get
    requests.post = mock.post
    mock.set_get_response(json.dumps(dict(one=dict(scans=[1, 2, 3]))), 200)
    mock.set_post_response("Not OK", 400)
    assert _run(doc, args(ids=["one"], noconfirm=True)) == (None, 1)
    assert mock.last_post_rq == ("http://localhost:8123/remove", {"ids": ["one"]}, None)
    out, err = capfd.readouterr()
    assert err == ""
    out = out.split("\n")
    assert out[0] == "You are about to delete 1 document (3 scans)."
    assert out[1] == "Remove failed with code 400: Not OK"


def test_rm_notyes(capfd, with_test_config):
    doc = docman.Document.load({})
    mock = RequestsMock()
    requests.get = mock.get
    # response for id lookup
    mock.set_get_response(json.dumps(dict(some_id=dict(scans=[1, 2, 3]))), 200)

    with replace_stdin("ye"):
        assert _run(doc, args(ids=["some_id"], noconfirm=False)) == (None, 1)
    out, err = capfd.readouterr()
    assert err == ""
    out = out.split("\n")
    assert out[0] == "You are about to delete 1 document (3 scans)."
    assert out[1] == "If you wish to continue, please type yes: Aborting..."
