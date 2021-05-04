def query(subparser):
    parser = subparser.add_parser(
        "query", description="Search for documents in database."
    )
    ### FILTER OPTIONS ###
    parser.add_argument(
        "--text",
        metavar="text",
        default="",
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
        dest="from_",
        metavar="yyyy-mm-dd",
        required=False,
        help="start date",
    )
    parser.add_argument(
        "--until",
        metavar="yyyy-mm-dd",
        required=False,
        help="end date",
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
        action="store_false",
        help="don't print table header",
    )
    parser.add_argument(
        "-r",
        "--raw",
        action="store_true",
        help="return raw json data",
    )
    parser.set_defaults(function=_run)


def _run(args):
    import sys
    import requests
    import docman.utils
    import datetime as dt

    # Build query
    query = {}
    try:
        if args.from_ is not None:
            query["start_date"] = dt.date.fromisoformat(args.from_)
        if args.until is not None:
            query["end_date"] = dt.date.fromisoformat(args.until)
    except ValueError:
        print("Date must be in YYYY-MM-DD format.")
        exit(1)

    if args.tags is not None:
        query["tags"] = args.tags.strip().lower().split(",")
    query["text"] = args.text.strip()
    config = docman.utils.get_config()["SERVER"]
    url = f"http://{config['address']}:{config['port']}/query"

    response = requests.get(url, json=query)
    if response.status_code != 200:
        print(f"Failed to connect to backend! (code {response.status_code})")
        print(response.text)
        sys.exit(1)
    if args.short:
        # print only IDs
        print("\n".join(list(response.json().keys())))
    elif args.raw:
        # print raw json
        print(response.text)
    else:
        # print full table
        import pandas as pd

        df = pd.DataFrame(response.json().values())
        # df.set_index("_id", drop=True, inplace=True)
        df["tags"] = df["tags"].apply(lambda x: ",".join(x))
        df["title"] = df["title"].apply(
            lambda x: " ".join([w.capitalize() for w in x.split("_")])
        )
        print(df[["_id", "date", "title", "tags"]].to_string(header=args.Q))
