def mode(subparser):
    parser = subparser.add_parser(
        "mode",
        description="Change the edit mode. "
        "You can think of it as 'what are your intentions when pushing to the server?'. "
        "Do you want to 'add' a new document? "
        "Do you want to 'update' the metadata (title, tags, text, date) of an existing document or "
        "do you want to 'replace' an existing document entirely including metadata and all its files?",
    )
    parser.add_argument(
        "mode",
        choices=["add", "update", "replace"],
        help="edit mode",
    )
    parser.add_argument(
        "--id",
        required=False,
        help="document id",
    )
    parser.set_defaults(function=_run)


def _run(doc, args):
    doc.mode = args.mode

    if args.id:
        doc._id = args.id

    if doc.mode == "add" and doc._id is not None:
        # add with id is not supported but won't throw error
        # also id is kept so when changing back to another mode won't require an id anymore
        print(
            "Warning: Adding a document for a given ID is not supported. "
            "The specified id will be ignored."
        )
    elif doc.mode != "add" and doc._id is None:
        # change without id doesn't work
        print(
            "Error: When choosing a mode other than 'add', an existing document id is required!"
        )
        exit(1)
    return doc
