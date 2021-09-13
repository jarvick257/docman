class Pull:
    @classmethod
    def add_parser(cls, subparser):
        parser = subparser.add_parser(
            "pull",
            description="Downloads document files to local machine (scans or PDFs)",
        )
        parser.add_argument(
            "id",
            help="document id",
        )
        parser.add_argument(
            "--output",
            "-o",
            metavar="directory",
            default=".",
            help="specify download directory (default: current directory)",
        )
        parser.set_defaults(function=cls.run)

    @classmethod
    def run(cls, doc, _id, output="."):
        import os
        import requests
        import urllib.request

        # get document info
        url = doc.server_url
        try:
            response = requests.get(f"{url}/query", json=dict(id=_id))
        except:
            print(f"Failed to connect to {url}/query")
            return None, 1
        if response.status_code != 200 or response.json() == {}:
            print(f"Didn't find any document for id {_id}")
            return None, 1
        meta = response.json()[_id]

        # Include PDF
        url = f"{url}/pdf/{meta['pdf']}"
        path = os.path.join(args.output, meta["pdf"])
        print(f"Downloading {path}")
        urllib.request.urlretrieve(url, filename=path)
        return None, 0
