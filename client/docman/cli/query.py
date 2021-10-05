class Query:
    @classmethod
    def add_parser(cls, subparser):
        parser = subparser.add_parser(
            "query", description="Search for documents in database."
        )
        ### FILTER OPTIONS ###
        parser.add_argument(
            "--id",
            dest="_id",
            metavar="ID",
            required=False,
            help="document id",
        )
        parser.add_argument(
            "--text",
            metavar="text",
            required=False,
            help="text to search",
        )
        parser.add_argument(
            "--tags",
            metavar="tag1,tag2,...",
            required=False,
            help="comma-separated list of tags",
        )
        parser.add_argument(
            "--from",
            dest="date_from",
            metavar="yyyy-mm-dd",
            required=False,
            help="include only documents after this date",
        )
        parser.add_argument(
            "--until",
            dest="date_until",
            metavar="yyyy-mm-dd",
            required=False,
            help="include only documents before this date",
        )
        ### OUTPUT OPTIONS ###
        parser.add_argument(
            "-q",
            "--short",
            action="store_true",
            help="only return document ids",
        )
        parser.add_argument(
            "-Q",
            "--no_header",
            action="store_true",
            help="don't print table header",
        )
        parser.add_argument(
            "-r",
            "--raw",
            action="store_true",
            help="return raw json data",
        )
        parser.set_defaults(function=cls.run)

    @classmethod
    def run(
        cls,
        doc,
        _id=None,
        text=None,
        tags=None,
        date_from=None,
        date_until=None,
        short=False,
        no_header=False,
        raw=False,
        **kwargs,
    ):
        import requests
        import datetime as dt

        # Get query
        query = {}
        try:
            if date_from is not None:
                # query["date_from"] = dt.date.fromisoformat(date_from)
                query["date_from"] = str(
                    dt.datetime.strptime(date_from, "%Y-%m-%d").date()
                )
            if date_until is not None:
                # query["date_until"] = dt.date.fromisoformat(date_until)
                query["date_until"] = str(
                    dt.datetime.strptime(date_until, "%Y-%m-%d").date()
                )
        except ValueError:
            print("Date must be in YYYY-MM-DD format.")
            return 1
        if _id is not None:
            query["id"] = _id.strip()
        if tags is not None:
            query["tags"] = tags.strip().lower().split(",")
        if text is not None:
            query["text"] = text.strip()

        # Get url
        url = f"{doc.server_url}/query"

        # Get results
        try:
            response = requests.get(url, json=query)
        except:
            print(f"Failed to connect to {url}")
            return 1
        if response.status_code != 200:
            print(f"Failed to connect to backend! (code {response.status_code})")
            # print(response.text)
            return 1

        # Print
        # print only IDs
        if short:
            print("\n".join(list(response.json().keys())))
            return 0

        # print raw json
        if raw:
            print(response.text)
            return 0

        # print full table
        import pandas as pd

        df = pd.DataFrame(response.json().values())
        if df.empty:
            print("No results")
            return 0
        df["tags"] = df["tags"].apply(lambda x: ",".join(x))
        df["title"] = df["title"].apply(
            lambda x: " ".join([w.capitalize() for w in x.split("_")])
        )
        print(df[["_id", "date", "title", "tags"]].to_string(header=not no_header))
        return 0
