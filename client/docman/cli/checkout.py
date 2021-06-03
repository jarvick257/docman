def checkout(subparser):
    parser = subparser.add_parser(
        "checkout",
        description="Loads documents from server into working directory",
    )
    parser.add_argument(
        "id",
        help="document id",
    )
    parser.set_defaults(function=_run)


def _run(args):
    import os
    import json
    import sys
    import requests
    import urllib.request
    from docman import Document
    from docman.utils import get_config
    from progress.bar import Bar

    doc = Document.load()
    # don't overwrite existing document
    if doc.is_wip():
        print(
            "Refusing to checkout: Current working directory not empty.\n"
            "Push current document with 'docman push' or discard everything with"
            "'docman reset --hard'"
        )
        sys.exit(1)

    # get document info
    config = get_config()
    url = f"http://{config['SERVER']['address']}:{config['SERVER']['port']}"
    response = requests.get(f"{url}/query", json=dict(id=args.id))
    if response.status_code != 200 or response.json() == {}:
        print(f"Didn't find any document for id {args.id}")
        sys.exit(1)
    meta = response.json()[args.id]
    files = [(f"{url}/pdf/{meta['pdf']}", "combined.pdf")]
    for scan in meta["scans"]:
        files.append((f"{url}/scan/{scan}", scan))
    print(json.dumps(meta, indent=2))

    bar = Bar("Checking out files", max=len(files))
    for i, (url, path) in enumerate(files):
        bar.next(i)
        urllib.request.urlretrieve(url, filename=os.path.join(doc.wd, path))
    bar.next()
    bar.finish()
    doc = Document.load(meta)
    doc.save()
