def reset(subparser):
    parser = subparser.add_parser(
        "reset",
        description="Resets working state (by default, existing scans are kept)",
    )
    parser.add_argument(
        "--hard",
        action="store_true",
        help="delete all files, including scans",
    )
    parser.set_defaults(function=_run)


def _run(doc, args):
    from datetime import date
    import glob
    import os
    from docman import Document

    doc = Document.load({})
    if not args.hard:
        doc.scans = sorted(glob.glob(os.path.join(doc.wd, "*.jpg")))
    return doc
