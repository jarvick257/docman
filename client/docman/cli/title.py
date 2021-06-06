def title(subparser):
    parser = subparser.add_parser("title", description="Sets the document title.")
    parser.add_argument(
        "--clear",
        action="store_true",
        help="clears the title without setting a new one",
    )
    parser.add_argument("title", nargs="*", help="title of the document")
    parser.set_defaults(function=_run)


def _run(doc, args):
    if args.clear:
        doc.title = None
    elif args.title != []:
        # When title is passed as multiple args
        title = "_".join(args.title)
        # When title is passed as single arg (eg in quotes)
        title = title.replace(" ", "_")
        doc.title = title
    print("" if doc.title is None else doc.title)
    return doc, 0
