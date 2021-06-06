def checkout(subparser):
    parser = subparser.add_parser(
        "checkout", description="Loads documents from server into working directory."
    )
    parser.add_argument("id", help="document id")
    parser.add_argument(
        "--update",
        action="store_true",
        help="checkout in 'update' mode. This will only download meta data and no actual files.",
    )
    parser.set_defaults(function=_run)


def _run(doc, args):
    import os
    import json
    import requests
    import urllib.request

    from docman import Document
    from progress.bar import Bar

    # don't overwrite existing document
    if doc.is_wip():
        print(
            "Refusing to checkout: Current working directory not empty.\n"
            "Push current document with 'docman push' or discard everything with "
            "'docman reset --hard'"
        )
        return None, 1

    # get document info
    response = requests.get(f"{doc.server_url}/query", json=dict(id=args.id))
    if response.status_code != 200 or response.json() == {}:
        print(f"Didn't find any document for id {args.id}")
        return None, 1

    # Create document
    meta = response.json()[args.id]
    doc = Document.load(meta)
    # fix paths
    doc.pdf = os.path.join(doc.wd, "combined.pdf")
    doc.scans = [os.path.join(doc.wd, scan) for scan in doc.scans]
    doc.mode = "update" if args.update else "replace"

    # for edit only, we're done. Otherwise we need to download some files, too
    if args.update:
        return doc, 0

    # create file list as tuple (url, save path)
    files = [(f"{doc.server_url}/pdf/{meta['pdf']}", "combined.pdf")]
    for scan in meta["scans"]:
        files.append((f"{doc.server_url}/scan/{scan}", scan))
    # Download files
    bar = Bar("Checking out files", max=len(files))
    for i, (url, path) in enumerate(files):
        bar.next()
        urllib.request.urlretrieve(url, filename=os.path.join(doc.wd, path))
    bar.finish()
    return doc, 0
