def pull(subparser):
    parser = subparser.add_parser(
        "pull",
        description="Downloads document files to local machine (scans or PDFs)",
    )
    parser.add_argument(
        "id",
        help="document id",
    )
    parser.add_argument(
        "--scans", action="store_true", help="download scan files instead of PDF"
    )
    parser.add_argument(
        "--all", action="store_true", help="download all files (scans and PDFs)"
    )
    parser.add_argument(
        "--output",
        "-o",
        metavar="directory",
        default=".",
        help="specify download directory (default: current directory)",
    )
    parser.set_defaults(function=_run)


def _run(args):
    import os
    import json
    import sys
    import requests
    import urllib.request
    from docman.utils import get_config

    # get document info
    config = get_config()
    url = f"http://{config['SERVER']['address']}:{config['SERVER']['port']}"
    response = requests.get(f"{url}/query", json=dict(id=args.id))
    if response.status_code != 200 or response.json() == {}:
        print(f"Didn't find any document for id {args.id}")
        sys.exit(1)
    meta = response.json()[args.id]

    # Create file list
    files = []
    if args.all or args.scans:
        # Include scans
        for scan in meta["scans"]:
            files.append((f"{url}/scan/{scan}", os.path.join(args.output, scan)))
    if args.all or not args.scans:
        # Include PDF
        files.append(
            (f"{url}/pdf/{meta['pdf']}", os.path.join(args.output, meta["pdf"]))
        )

    for i, (url, path) in enumerate(files):
        print(f"Downloading {i+1}/{len(files)}: {path}")
        urllib.request.urlretrieve(url, filename=path)
