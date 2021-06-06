def preview(subparser):
    parser = subparser.add_parser(
        "preview",
        description="Previews scans or PDFs from the current working state.",
    )
    parser.add_argument(
        "selection",
        nargs="*",
        choices=["auto", "scans", "pdf"],
        help="preview documents",
        default="auto",
    )
    parser.set_defaults(function=_run)


def _run(doc, args):
    import os

    if (args.selection == ["pdf"] or args.selection == "auto") and doc.pdf is not None:
        print("Previewing pdf")
        cmd = doc.config["INTEGRATION"]["pdf_preview"]
        os.system(f"{cmd} {doc.pdf}")
    elif (args.selection == ["scans"] or args.selection == "auto") and doc.scans != []:
        print("Previewing scans")
        cmd = doc.config["INTEGRATION"]["image_preview"]
        files = " ".join(doc.scans)
        os.system(f"{cmd} {files}")
    else:
        print("Nothing to preview")
    exit(0)  # no need to save
