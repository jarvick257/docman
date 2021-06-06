def date(subparser):
    parser = subparser.add_parser("date", description="Sets the document date.")
    parser.add_argument("date", nargs="*", metavar="YYYY-MM-DD", help="document date")
    parser.set_defaults(function=_run)


def _run(doc, args):
    import datetime as dt

    try:
        # try converting to date to check format
        new_date = "-".join(args.date).replace(" ", "-")
        # fromisoformat only available in python3.7
        # new_date = str(dt.date.fromisoformat(new_date))
        new_date = str(dt.datetime.strptime(new_date, "%Y-%m-%d").date())
        print(f"Set document date to {new_date}")
    except ValueError:
        print("Date must be in YYYY-MM-DD format.")
        return None, 1
    doc.date = new_date
    return doc, 0
