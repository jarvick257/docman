def scan(subparser):
    parser = subparser.add_parser(
        "scan",
        description="""Adds new files to the current working state."""
        """ When scan is called after ocr or pdf, existing ocr and pdf data will be deleted.""",
    )
    parser.set_defaults(function=_run)


def _run(doc, args):
    import os
    from datetime import datetime
    from subprocess import check_call

    timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    output = os.path.join(doc.wd, f"{timestamp}.jpg")
    command_template = doc.config["INTEGRATION"]["scan"]
    cmd = command_template.replace("{file}", output)
    print(cmd)
    check_call(cmd.split())
    if doc.pdf is not None:
        doc.pdf = None
        print("Scans changed! Removed existing PDF")
    if doc.ocr is not None:
        doc.ocr = None
        print("Scans changed! Removed existing OCR")
    doc.scans.append(output)
    return doc
