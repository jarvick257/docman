def push(subparser):
    parser = subparser.add_parser(
        "push",
        description="""Pushes the current working state to the docman server and resets. """
        """If push is called before pdf or ocr, these steps will be automatically performed using default arguments. """,
    )
    parser.add_argument(
        "--replace",
        action="store_true",
        help="replace existing documents (only relevant after checkout)",
    )
    parser.add_argument(
        "--add",
        action="store_true",
        help="treat document as if it was new (only relevant after checkout)",
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
    if doc.mode == "add" or doc.mode == "replace":
        if doc.scans == [] or doc.tags == [] or doc.title is None:
            print("Document is not ready to be pushed!")
            print(
                "Make sure you have at least one scan, one ore more tags and a title."
            )
            exit(1)
        if doc.ocr is None:
            ocr_args = namedtuple("fake_args", ("lang", "max_jobs"))(None, 4)
            doc = ocr(doc, ocr_args)
        if not doc.pdf:
            doc = pdf(doc, None)
    elif doc.mode == "update":
        if (
            doc._id is None
            or doc.tags == []
            or doc.title is None
            or doc.date is None
            or doc.ocr is None
        ):
            print("Document is not ready to be pushed!")
            print("Required attributes: id, tags, title, date, ocr")
            exit(1)
    else:
        print(f"Unrecognized mode: {mode}")
        exit(1)

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
            raise
    elif doc.mode == "update":
        try:
            r = requests.post(f"{doc.server_url}/{doc.mode}", json=post)
        except:
            print(f"Failed to connect to server!")
            raise

    if r.status_code == 201:
        # need an object with "hard" property set to True
        fake_args = namedtuple("Args", "hard")(True)
        doc = reset(doc, fake_args)
        print("Push successful")
        return doc
    else:
        print(f"Push failed with code {r.status_code}: {r.text}")
        exit(1)
