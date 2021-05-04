def scan(subparser):
    parser = subparser.add_parser(
        "scan",
        description="""Adds new files to the current working state."""
        """ When scan is called after ocr or pdf, existing ocr and pdf data will be deleted.""",
    )
    parser.add_argument(
        "--format", help="choose the file format of the scan", default="jpeg"
    )
    parser.set_defaults(function=_run)


def _run(args):
    import os
    from datetime import datetime
    from docman import Document

    # The illusion of choice
    if args.format not in ["jpeg"]:
        raise NotImplementedError

    doc = Document.load()
    command_template = doc.config["INTEGRATION"]["scan"]
    timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    output = os.path.join(doc.wd, f"{timestamp}.jpg")
    cmd = command_template.replace("{fmt}", args.format)
    cmd = cmd.replace("{file}", output)
    print(cmd)
    os.system(cmd)
    if doc.pdf is not None:
        os.remove(doc.pdf)
        doc.pdf = None
        print("Scans changed! Removed existing PDF")
    if doc.ocr is not None:
        os.remove(doc.ocr)
        doc.ocr = None
        print("Scans changed! Removed existing OCR")
    doc.scans.append(output)
    doc.save()
