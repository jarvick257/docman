from collections import namedtuple
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


def test_query_noarg(with_test_config):
    doc = docman.Document.load({})
    mock = RequestsMock()
    requests.get = mock.get
    mock.set_get_response("{}", 200)
    assert _run(doc, args()) == (None, 0)
    assert mock.last_get_rq == ("http://localhost:8123/query", {}, None)


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
