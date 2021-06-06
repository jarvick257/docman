import os
import configparser

_configpath = None


def _create_default_config():
    path = get_config_path()
    dir = os.path.dirname(path)
    if not os.path.isdir(dir):
        os.makedirs(dir)
    config = configparser.ConfigParser()
    config["DEFAULT"] = {"working_dir": "/tmp/docman", "default_language": "eng"}
    config["SERVER"] = {"address": "localhost", "port": "8123"}
    config["INTEGRATION"] = {
        "scan": "scanimage --device airscan:w0:HP --format jpg --output-file {file} --progress",
        "image_preview": "feh",
        "pdf_preview": os.environ.get("BROWSER", "firefox"),
    }
    with open(path, "w") as configfile:
        config.write(configfile)
    return config


def set_config_path(path):
    global _configpath
    _configpath = path


def get_config_path():
    global _configpath
    if _configpath is None:
        _configpath = os.path.join(
            os.environ["HOME"], ".config", "docman", "docman.conf"
        )
    return _configpath


def get_config():
    path = get_config_path()
    if not os.path.isfile(path):
        return _create_default_config()
    config = configparser.ConfigParser()
    config.read(path)
    return config
