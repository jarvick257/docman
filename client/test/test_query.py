from collections import namedtuple
import json
import requests
import pytest

import docman
from docman.cli.query import _run
from testhelpers import RequestsMock, with_test_config


def args(**kwargs):
    fake_args = namedtuple(
        "args", ("id", "text", "tags", "date_from", "date_until", "short", "Q", "raw")
    )
    return fake_args(
        kwargs.get("id", None),
        kwargs.get("text", None),
        kwargs.get("tags", None),
        kwargs.get("date_from", None),
        kwargs.get("date_until", None),
        kwargs.get("short", False),
        kwargs.get("Q", True),
        kwargs.get("raw", False),
    )


def test_query_noarg(capfd, with_test_config):
    doc = docman.Document.load({})
    mock = RequestsMock()
    requests.get = mock.get
    mock.set_get_response("{}", 200)
    assert _run(doc, args()) == (None, 0)
    assert mock.last_get_rq == ("http://localhost:8123/query", {}, None)
    out, err = capfd.readouterr()
    assert err == ""
    assert out == "No results\n"


def test_query_args(with_test_config):
    doc = docman.Document.load({})
    mock = RequestsMock()
    requests.get = mock.get
    mock.set_get_response("{}", 200)
    args_d = dict(
        id="id",
        text="text",
        tags="some,tags",
        date_from="2020-01-01",
        date_until="2023-01-01",
    )
    assert (
        _run(
            doc,
            args(**args_d),
        )
        == (None, 0)
    )
    # request data is same as arguments except tags are split
    req_d = args_d
    req_d["tags"] = ["some", "tags"]
    assert mock.last_get_rq == ("http://localhost:8123/query", req_d, None)


def test_query_wrong_date(capfd, with_test_config):
    doc = docman.Document.load({})
    mock = RequestsMock()
    requests.get = mock.get
    mock.set_get_response("{}", 200)
    assert _run(doc, args(date_from="20201201")) == (None, 1)
    out, err = capfd.readouterr()
    assert err == ""
    assert out == "Date must be in YYYY-MM-DD format.\n"

    doc = docman.Document.load({})
    mock = RequestsMock()
    requests.get = mock.get
    mock.set_get_response("{}", 200)
    assert _run(doc, args(date_until="2020-13-01")) == (None, 1)
    out, err = capfd.readouterr()
    assert err == ""
    assert out == "Date must be in YYYY-MM-DD format.\n"


def test_query_failed(capfd, with_test_config):
    # Retval
    doc = docman.Document.load({})
    mock = RequestsMock()
    requests.get = mock.get
    mock.set_get_response("{}", 201)
    assert _run(doc, args()) == (None, 1)
    out, err = capfd.readouterr()
    assert err == ""
    assert out == "Failed to connect to backend! (code 201)\n"

    # exception
    doc = docman.Document.load({})
    mock = RequestsMock()
    requests.get = mock.get
    mock.set_get_response("{}", requests.exceptions.ConnectionError)
    assert _run(doc, args()) == (None, 1)
    out, err = capfd.readouterr()
    assert err == ""
    assert out == "Failed to connect to http://localhost:8123/query\n"


def test_query_short(capfd, with_test_config):
    doc = docman.Document.load({})
    mock = RequestsMock()
    requests.get = mock.get
    result = dict(one=dict(), two=dict())
    mock.set_get_response(json.dumps(result), 200)
    assert _run(doc, args(short=True)) == (None, 0)
    out, err = capfd.readouterr()
    assert err == ""
    assert out == "one\ntwo\n"


def test_query_raw(capfd, with_test_config):
    doc = docman.Document.load({})
    mock = RequestsMock()
    requests.get = mock.get
    result = dict(one=dict(), two=dict())
    mock.set_get_response(json.dumps(result), 200)
    assert _run(doc, args(raw=True)) == (None, 0)
    out, err = capfd.readouterr()
    assert err == ""
    assert out == json.dumps(result) + "\n"


def test_query_table(capfd, with_test_config):
    doc = docman.Document.load({})
    mock = RequestsMock()
    requests.get = mock.get
    result = dict(
        one=dict(tags=["a", "b"], title="one", _id="idone", date="dateone"),
        two=dict(tags=["c", "d"], title="two", _id="idtwo", date="datetwo"),
    )
    mock.set_get_response(json.dumps(result), 200)
    assert _run(doc, args()) == (None, 0)
    out, err = capfd.readouterr()
    assert err == ""
    out = out.split("\n")
    assert out[0] == "     _id     date title tags"
    assert out[1] == "0  idone  dateone   One  a,b"
    assert out[2] == "1  idtwo  datetwo   Two  c,d"
