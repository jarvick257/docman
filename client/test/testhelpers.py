import os
import pytest
import docman
import requests
import sys
from io import StringIO
from contextlib import contextmanager

from collections import deque


class RequestsMock:
    def __init__(self):
        # URL, data, files
        self.last_get_rq = (None, None, None)
        self.last_post_rq = (None, None, None)
        self.get_response = deque()
        self.post_response = deque()

    def get(self, *args, **kwargs):
        url = args[0]
        data = kwargs.get("json", None)
        files = kwargs.get("files", None)
        self.last_get_rq = (url, data, files)
        r = self.get_response.popleft()
        if not isinstance(r.status_code, int):
            raise r.status_code
        return r

    def post(self, *args, **kwargs):
        url = args[0]
        data = kwargs.get("json", None)
        files = kwargs.get("files", None)
        self.last_post_rq = (url, data, files)
        return self.post_response.popleft()

    def set_get_response(self, txt, code):
        r = requests.Response()
        r.status_code = code
        r._content = txt.encode()
        self.get_response.append(r)

    def set_post_response(self, txt, code):
        r = requests.Response()
        r.status_code = code
        r._content = txt.encode()
        self.post_response.append(r)


@contextmanager
def replace_stdin(target):
    target = StringIO(target)
    orig = sys.stdin
    sys.stdin = target
    yield
    sys.stdin = orig


@pytest.fixture
def with_test_config():
    os.system("rm -rf /tmp/test_docman")
    test_dir = os.path.dirname(__file__)
    docman.utils.set_config_path(f"{test_dir}/config.ini")
