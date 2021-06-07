def query(subparser):
    parser = subparser.add_parser(
        "query", description="Search for documents in database."
    )
    ### FILTER OPTIONS ###
    parser.add_argument(
        "--id",
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


def _run(doc, args):
    import requests
    import datetime as dt

    # Get query
    query = {}
    try:
        if args.date_from is not None:
            # query["date_from"] = dt.date.fromisoformat(args.date_from)
            query["date_from"] = str(
                dt.datetime.strptime(args.date_from, "%Y-%m-%d").date()
            )
        if args.date_until is not None:
            # query["date_until"] = dt.date.fromisoformat(args.date_until)
            query["date_until"] = str(
                dt.datetime.strptime(args.date_until, "%Y-%m-%d").date()
            )
    except ValueError:
        print("Date must be in YYYY-MM-DD format.")
        return None, 1
    if args.id is not None:
        query["id"] = args.id.strip()
    if args.tags is not None:
        query["tags"] = args.tags.strip().lower().split(",")
    if args.text is not None:
        query["text"] = args.text.strip()

    # Get url
    url = f"{doc.server_url}/query"

    # Get results
    try:
        response = requests.get(url, json=query)
    except:
        print(f"Failed to connect to {url}")
        return None, 1
    if response.status_code != 200:
        print(f"Failed to connect to backend! (code {response.status_code})")
        # print(response.text)
        return None, 1

    # Print
    # print only IDs
    if args.short:
        print("\n".join(list(response.json().keys())))
        return None, 0

    # print raw json
    if args.raw:
        print(response.text)
        return None, 0

    # print full table
    import pandas as pd

    df = pd.DataFrame(response.json().values())
    if df.empty:
        print("No results")
        return None, 0
    df["tags"] = df["tags"].apply(lambda x: ",".join(x))
    df["title"] = df["title"].apply(
        lambda x: " ".join([w.capitalize() for w in x.split("_")])
    )
    print(df[["_id", "date", "title", "tags"]].to_string(header=args.Q))
    return None, 0
