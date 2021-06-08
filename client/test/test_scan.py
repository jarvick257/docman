from datetime import datetime
import pytest

import docman
from docman.cli.scan import _run


def get_default_doc():
    cmd_template = "echo scancmd {file}"
    doc = docman.Document()
    doc.wd = "/tmp/docman"
    doc.config = {"INTEGRATION": {"scan": cmd_template}}
    return doc


def test_scan_noarg(capfd):
    doc = get_default_doc()
    timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    assert doc.scans == []
    doc, retval = _run(doc, None)
    cmd = f"scancmd {doc.wd}/{timestamp}.jpg"
    assert retval == 0
    assert capfd.readouterr() == (f"echo {cmd}\n{cmd}\n", "")
    assert doc.scans == [f"{doc.wd}/{timestamp}.jpg"]


def test_scan_reset(capfd):
    doc = get_default_doc()
    doc.ocr = "some ocr"
    doc.pdf = "some pdf"
    timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    doc, retval = _run(doc, None)

    cmd = f"scancmd {doc.wd}/{timestamp}.jpg"
    assert retval == 0
    assert doc.scans == [f"{doc.wd}/{timestamp}.jpg"]
    assert doc.pdf == None
    assert doc.ocr == None
    out, err = capfd.readouterr()
    assert err == ""
    out = out.split("\n")
    assert out[0] == f"echo {cmd}"  # full command
    assert out[1] == f"{cmd}"  # command execution
    assert out[2] == "Scans changed! Removed existing PDF"  # pdf warning
    assert out[3] == "Scans changed! Removed existing OCR"  # ocr warning


def test_scan_fail_retval(capfd):
    doc = get_default_doc()
    doc.config["INTEGRATION"]["scan"] = "python -c exit(1)"
    doc.pdf = "some_pdf"
    doc, retval = _run(doc, None)
    assert retval == 1
    assert doc is None
    assert capfd.readouterr() == (
        "python -c exit(1)\npython -c exit(1) failed with return value 1!\n",
        "",
    )


def test_scan_fail_unknown(capfd):
    doc = get_default_doc()
    doc.config["INTEGRATION"]["scan"] = "nonexistingcommand some_arg"
    doc.pdf = "some_pdf"
    doc, retval = _run(doc, None)
    assert retval == 1
    assert doc is None
    assert capfd.readouterr() == (
        "nonexistingcommand some_arg\nnonexistingcommand doesn't exist!\n",
        "",
    )
