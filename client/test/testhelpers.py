import os
import pytest
import docman
import requests


class RequestsMock:
    def __init__(self):
        self.url = None
        self.data = None
        self.files = None
        self.response = requests.Response()

    def get(self, *args, **kwargs):
        self.url = args[0]
        self.data = kwargs.get("json", None)
        self.files = kwargs.get("files", None)
        return self.response

    def set_response(self, txt, code):
        self.response.status_code = code
        self.response._content = txt.encode()


@pytest.fixture
def with_test_config():
    os.system("rm -rf /tmp/test_docman")
    test_dir = os.path.dirname(__file__)
    docman.utils.set_config_path(f"{test_dir}/config.ini")
