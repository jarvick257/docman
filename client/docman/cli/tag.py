def tag(subparser):
    parser = subparser.add_parser(
        "tag", description="Adds or removes tags from document."
    )
    parser.add_argument("--clear", action="store_true", help="clear all tags")
    parser.add_argument("--list", action="store_true", help="lists all tags")
    parser.add_argument(
        "--remove",
        nargs="*",
        metavar="tag",
        help="removes tags",
        required=False,
        default=[],
    )
    parser.add_argument(
        "--add", nargs="*", metavar="tag", help="adds tags", required=False, default=[]
    )
    parser.add_argument("tags", nargs="*", help="adds tags", default=[])
    parser.set_defaults(function=_run)


def _run(args):
    from docman import Document

    if main_args == []:
        parser.print_help()
        exit(1)

    doc = Document.load()
    doctags = set(doc.tags)
    if args.clear:
        doctags.clear()
    for tag in args.remove:
        if tag in doctags:
            doctags.remove(tag)
    for tag in args.tags + args.add:
        doctags.add(tag.lower().replace(" ", "_"))
    doc.tags = list(doctags)
    print("Tags:", None if doc.tags == [] else ", ".join(sorted(doc.tags)))
    doc.save()
