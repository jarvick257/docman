class Checkout:
    @classmethod
    def add_parser(cls, subparser):
        parser = subparser.add_parser(
            "checkout",
            description="Loads documents from server into working directory.",
        )
        parser.add_argument("id", help="document id")
        parser.add_argument(
            "--update",
            action="store_true",
            help="checkout in 'update' mode. This will only download meta data and no actual files.",
        )
        parser.set_defaults(function=cls.run)

    @classmethod
    def run(cls, doc, _id, update=False):
        import os
        import json
        import requests
        import urllib.request

        from docman import Document

        # don't overwrite existing document
        if doc.is_wip():
            print(
                "Refusing to checkout: Current working directory not empty.\n"
                "Push current document with 'docman push' or discard everything with "
                "'docman reset --hard'"
            )
            return None, 1

        # get document info
        try:
            response = requests.get(f"{doc.server_url}/query", json=dict(id=_id))
        except:
            print(f"Failed to connect to {doc.server_url}/query")
            return None, 1
        if response.status_code != 200 or response.json() == {}:
            print(f"Didn't find any document for id {_id}")
            return None, 1

        # Create document
        meta = response.json()[_id]
        doc = Document.load(meta)
        # fix paths
        doc.pdf = os.path.join(doc.wd, "combined.pdf")
        doc.scans = [os.path.join(doc.wd, scan) for scan in doc.scans]
        doc.mode = "update" if update else "replace"

        # for edit only, we're done. Otherwise we need to download some files, too
        if update:
            print(doc._id)
            return doc, 0

        # create file list as tuple (url, save path)
        files = [(f"{doc.server_url}/pdf/{meta['pdf']}", "combined.pdf")]
        for scan in meta["scans"]:
            files.append((f"{doc.server_url}/scan/{scan}", scan))
        # Download files
        N = len(files)
        max_strlen = 0
        for i, (url, path) in enumerate(files):
            s = f"\rDownloading {i+1}/{N}"
            max_strlen = max(len(s), max_strlen)
            print(s, end="")
            urllib.request.urlretrieve(url, filename=os.path.join(doc.wd, path))
        padding = max_strlen - len(doc._id)
        print("\r" + doc._id + " " * padding)
        return doc, 0
