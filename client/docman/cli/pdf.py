def pdf(subparser):
    # only needed for --help
    parser = subparser.add_parser(
        "pdf", description="Combines scans into a single PDF."
    )
    parser.set_defaults(function=_run)


def _run(doc, args):
    import os

    if doc.scans == []:
        print("No scans!")
        exit(1)
    source_files = " ".join(doc.scans)
    output = os.path.join(doc.wd, "combined.pdf")
    cmd = f"convert {source_files} {output}"
    print(cmd)
    os.system(cmd)
    doc.pdf = output
    return doc
