import os

import pytest

import docman
from docman.cli.config import _run
from testhelpers import with_test_config

last_sys_call = None


def os_system_mock(cmd):
    global last_sys_call
    last_sys_call = cmd


def test_config(with_test_config):
    global last_sys_call
    orig_func = os.system
    os.system = os_system_mock
    test_dir = os.path.dirname(__file__)
    config = f"{test_dir}/config.ini"

    # with environ
    os.environ["EDITOR"] = "test_editor"
    doc = docman.Document.load({})
    assert _run(doc, None) == (None, 0)
    assert last_sys_call == f"test_editor {config}"

    # without environ
    del os.environ["EDITOR"]
    doc = docman.Document.load({})
    assert _run(doc, None) == (None, 0)
    assert last_sys_call == f"vi {config}"

    os.system = orig_func
