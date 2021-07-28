def status(subparser):
    parser = subparser.add_parser("status", description="Shows current working state")
    parser.add_argument("--json", action="store_true", help="show output as json")
    parser.add_argument("--full_ocr", action="store_true", help="show full ocr output")
    parser.set_defaults(function=_run)


def default_action(doc, args):
    # When run as default action, argparser doesn't pass
    # default arguments from subparser. So we have to set them here again.
    args.full_ocr = False
    args.json = False
    return _run(doc, args)


def _run(doc, args):
    import os

    if args.full_ocr:
        ocr_str = doc.ocr
    else:
        ocr_words = 0 if doc.ocr is None else len(doc.ocr.split(" "))
        ocr_str = f"{ocr_words} words"

    if args.json:
        import json

        # dump dict and we're done
        d = doc.to_dict()
        d["ocr"] = ocr_str
        print(json.dumps(d, indent=2))
        return None, 0

    if doc.mode == "add":
        mode = doc.mode
    else:
        mode = f"{doc.mode} {doc._id}"
    print(f"Mode:   {mode}")
    print(f"Title:  {doc.title}")
    print(f"Date:   {doc.date.date()}")
    print(f"Tags:   {'None' if doc.tags == [] else ' '.join(doc.tags)}")
    print(f"Inputs: {len(doc.input_files)}")
    for i in doc.input_files:
        print(f"    - {os.path.basename(i)}")
    print(f"Pdf:    {'Yes' if doc.pdf else 'No'}")
    return None, 0
