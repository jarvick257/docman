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


def _run(args):
    import os
    import requests
    import json
    from collections import namedtuple

    from docman import Document
    from .ocr import _run as ocr
    from .pdf import _run as pdf
    from .reset import _run as reset

    doc = Document.load()
    if doc.scans == [] or doc.tags == [] or doc.title is None:
        print("Document is not ready to be pushed!")
        print("Make sure you have at least one scan, one ore more tags and a title.")
        exit(1)
    if doc.ocr is None:
        ocr_args = namedtuple("fake_args", "lang", "max_jobs")(None, 4)
        ocr(ocr_args)
        doc = Document.load()
    if not doc.pdf:
        pdf(None)
        doc = Document.load()

    if args.replace and args.add:
        print("--replace and --add option are mutually exclusive!")
        exit(1)
    if doc._id is not None and not args.replace and not args.add:
        print("Either --replace or --add are required when pushing after checkout!")
        print("Run 'docman push --help' to learn more.")
        exit(1)

    # Prepare database post
    post = doc.to_dict()
    del post["pdf"]
    del post["scans"]
    if "_id" in post and args.add:
        # by deleting the id, the document will be treated as new
        del post["_id"]
    doc.post = os.path.join(doc.wd, "post.json")
    with open(doc.post, "w") as fp:
        json.dump(post, fp)
    files = [
        ("pdf", open(doc.pdf, "rb")),
        ("post", open(doc.post, "rb")),
    ]
    for scan in doc.scans:
        files.append(("scan", open(scan, "rb")))
    ip = doc.config["SERVER"]["address"]
    port = doc.config["SERVER"]["port"]
    try:
        r = requests.post(f"http://{ip}:{port}/add", files=files)
    except:
        print(f"Failed to connect to server!")
        raise
    if r.status_code == 201:
        # need an object with "hard" property set to True
        fake_args = namedtuple("Args", "hard")(True)
        reset(fake_args)
        print("Push successful")
        exit(0)
    else:
        print(f"Push failed with code {r.status_code}: {r.text}")
        exit(1)
