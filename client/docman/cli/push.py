def push(subparser):
    parser = subparser.add_parser(
        "push",
        description="""Pushes the current working state to the docman server and resets. """,
    )
    parser.set_defaults(function=_run)


def _run(doc, args):
    import os
    import requests
    import json
    from collections import namedtuple

    from .ocr import _run as ocr
    from .pdf import _run as pdf
    from .reset import _run as reset

    # Check for if ready to be pushed
    if not doc.is_complete():
        print("Document is not ready to be pushed!")
        print("For adding, you need tags, a title, a pdf, a date and ocr")
        print("For replacing, you need tags, a title, a pdf, a date, ocr and an id")
        print("For updating, you need tags, a title, a date, ocr and an id")
        return None, 1

    # Prepare post
    post = dict(title=doc.title, date=doc.date, tags=doc.tags, ocr=doc.ocr)
    if doc.mode == "update" or doc.mode == "replace":
        post["_id"] = doc._id
    if doc.mode == "add" or doc.mode == "replace":
        files = [
            ("post", json.dumps(post)),
            ("pdf", open(doc.pdf, "rb")),
        ]
        for scan in doc.scans:
            files.append(("scan", open(scan, "rb")))
        try:
            r = requests.post(f"{doc.server_url}/{doc.mode}", files=files)
        except:
            print(f"Failed to connect to server!")
            return None, 1
    elif doc.mode == "update":
        try:
            r = requests.post(f"{doc.server_url}/{doc.mode}", json=post)
        except:
            print(f"Failed to connect to server!")
            return None, 1

    if r.status_code == 201:
        # need an object with "hard" property set to True
        fake_args = namedtuple("Args", "hard")(True)
        doc, _ = reset(doc, fake_args)
        print("Push successful")
        return doc, 0
    else:
        print(f"Push failed with code {r.status_code}: {r.text}")
        return None, 1
