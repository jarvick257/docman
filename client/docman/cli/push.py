def push(subparser):
    parser = subparser.add_parser(
        "push",
        description="""Pushes the current working state to the docman server and resets. """
        """If push is called before pdf or ocr, these steps will be automatically performed using default arguments.""",
    )
    parser.set_defaults(function=_run)


def _run(args):
    import os
    import requests
    import json
    from docman import Document
    from docman.cli import ocr, pdf, reset

    doc = Document.load()
    if doc.scans == [] or doc.tags == [] or doc.title is None:
        print("Document is not ready to be pushed!")
        print("Make sure you have at least one scan, one ore more tags and a title.")
        exit(1)
    if doc.ocr is None:
        ocr([])
        doc = Document.load()
    if not doc.pdf:
        pdf([])
        doc = Document.load()

    # Prepare database post
    post = doc.to_dict()
    del post["pdf"]
    del post["scans"]
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
        if r.status_code == 201:
            print("Push successful")
            reset(["--hard"])
        else:
            print(f"Push failed with code {r.status_code}: {r.text}")
    except:
        print(f"Push failed!")
        raise
