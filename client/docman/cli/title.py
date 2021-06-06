def title(subparser):
    parser = subparser.add_parser("title", description="Sets the document title.")
    parser.add_argument(
        "--clear",
        action="store_true",
        help="clears the title without setting a new one",
    )
    parser.add_argument("title", nargs="*", help="title of the document")
    parser.set_defaults(function=_run)


def _run(args):
    from docman import Document

    if not args.clear and args.title == []:
        parser.print_help()
        exit(1)

    doc = Document.load()
    if args.clear:
        doc.title = None
        doc.save()
        print("Title was cleared")
        return

    # When title is passed as multiple args
    title = "_".join(args.title)
    # When title is passed as single arg (eg in quotes)
    title = title.replace(" ", "_")
    doc.title = title
    print(f"Title was set to {doc.title}")
    doc.save()
