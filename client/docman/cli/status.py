def status(subparser):
    parser = subparser.add_parser("status", description="Shows current working state")
    parser.add_argument("--json", action="store_true", help="show output as json")
    parser.add_argument("--full-ocr", action="store_true", help="show full ocr output")
    parser.set_defaults(function=_run)


def default_action(args):
    # When run as default action, argparser doesn't pass
    # default arguments from subparser. So we have to set them here again.
    args.full_ocr = False
    args.json = False
    _run(args)


def _run(args):
    import json
    from docman import Document

    doc = Document.load()
    if args.full_ocr:
        ocr_str = doc.ocr
    else:
        ocr_words = 0 if doc.ocr is None else len(doc.ocr.split(" "))
        ocr_str = f"{ocr_words} words"

    if args.json:
        d = doc.to_dict()
        d["ocr"] = ocr_str
        print(json.dumps(d, indent=2))
    else:
        print(f"Title: {doc.title}")
        print(f"Date:  {doc.date}")
        print(f"Tags:  {'None' if doc.tags == [] else ' '.join(doc.tags)}")
        print(f"Scans: {len(doc.scans)}")
        print(f"Ocr:   {ocr_str}")
        print(f"Pdf:   {'Yes' if doc.pdf else 'No'}")
