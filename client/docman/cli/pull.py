class Pull:
    @classmethod
    def add_parser(cls, subparser):
        parser = subparser.add_parser(
            "pull",
            description="Downloads document files to local machine (scans or PDFs)",
        )
        parser.add_argument(
            "_id",
            metavar="id",
            help="document id",
        )
        parser.add_argument(
            "--output",
            "-o",
            metavar="directory",
            default=".",
            help="specify download directory (default: current directory)",
        )
        parser.add_argument(
            "--keep_id",
            action="store_true",
            help="Use <id>.pdf scheme instead of <date>_<title>.pdf",
        )

        parser.set_defaults(function=cls.run)

    @classmethod
    def run(cls, doc, _id, output=".", keep_id=False, **kwargs):
        import os
        import requests
        from urllib.request import urlretrieve

        # get document info
        url = doc.server_url
        try:
            response = requests.get(f"{url}/query", json=dict(id=_id))
        except:
            print(f"Failed to connect to {url}/query")
            return 1
        if response.status_code != 200 or response.json() == {}:
            print(f"Didn't find any document for id {_id}")
            return 1
        meta = response.json()[_id]

        url = f"{url}/pdf/{meta['pdf']}"
        if not keep_id:
            path = os.path.join(output, meta["pdf"])
        else:
            path = os.path.join(output, meta["_id"] + ".pdf")
        urlretrieve(url, filename=path)
        print(path)
        return 0
