def pdf(subparser):
    # only needed for --help
    parser = subparser.add_parser(
        "pdf", description="Combines scans into a single PDF."
    )
    parser.set_defaults(function=_run)


def _run(doc, args):
    import os
    import subprocess as sp

    if doc.scans == []:
        print("No scans!")
        return None, 1
    source_files = " ".join(doc.scans)
    output = os.path.join(doc.wd, "combined.pdf")
    cmd = doc.config["INTEGRATION"]["pdf_conversion"]
    cmd = cmd.replace("{source_files}", source_files)
    cmd = cmd.replace("{output}", output)
    try:
        sp.check_call(cmd.split())
    except sp.CalledProcessError as e:
        print(f"{cmd} failed with return value {e.args[0]}!")
        return None, 1
    except FileNotFoundError as e:
        print(f"{cmd.split()[0]} doesn't exist!")
        return None, 1
    doc.pdf = output
    print(doc.pdf)
    return doc, 0
