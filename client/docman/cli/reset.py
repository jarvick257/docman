def reset(subparser):
    parser = subparser.add_parser(
        "reset",
        description="Resets working state.",
    )
    parser.add_argument(
        "--hard",
        action="store_true",
        help="deletes all files, including scans",
    )
    parser.set_defaults(function=_run)


def _run(args):
    from datetime import date
    import glob
    import os
    from docman import Document
    from docman.utils import get_config

    wd = get_config()["DEFAULT"]["working_dir"]
    if args.hard:
        for path in glob.glob(os.path.join(wd, "*")):
            os.remove(path)
        print("Cleared all files")
    else:
        doc = Document.load()
        doc.tags = []
        doc.title = None
        doc.ocr = None
        doc.date = str(date.today())
        doc.scans = sorted(glob.glob(os.path.join(doc.wd, "*.jpg")))
        doc.pdf = None
        for path in glob.glob(os.path.join(wd, "*.pdf")):
            os.remove(path)
        doc.save()
