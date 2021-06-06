import os
import pytest
import docman


@pytest.fixture
def with_test_config():
    os.system("rm -rf /tmp/test_docman")
    test_dir = os.path.dirname(__file__)
    docman.utils.set_config_path(f"{test_dir}/config.ini")
