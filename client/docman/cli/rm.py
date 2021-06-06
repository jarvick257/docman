def rm(subparser):
    parser = subparser.add_parser(
        "rm",
        description="Delete documents",
    )
    parser.add_argument(
        "ids",
        nargs="+",
        help="document id",
    )
    parser.add_argument(
        "--noconfirm",
        action="store_true",
        help="delete without asking for confirmation",
    )
    parser.set_defaults(function=_run)


def _run(doc, args):
    import os
    import json
    import requests

    url = doc.server_url

    # Check ids
    ids = []
    num_scans = 0
    for _id in set(args.ids):
        # get document info
        response = requests.get(f"{url}/query", json=dict(id=_id))
        if response.status_code != 200 or response.json() == {}:
            print(f"Warning: No document found for id {_id}")
            continue
        meta = response.json()[_id]
        ids.append(_id)
        num_scans += len(meta["scans"])

    if len(ids) == 0:
        print("Nothing to delete.")
        exit(0)

    # Ask for confirmation
    pl = "s" if len(ids) > 1 else ""
    print(f"You are about to delete {len(ids)} document{pl} ({num_scans} scan{pl}).")
    if not args.noconfirm:
        r = input("If you wish to continue, please type yes: ")
        if r.lower() != "yes":
            print("Aborting...")
            exit(1)

    # Delete
    r = requests.post(f"{url}/remove", json=dict(ids=ids))
    if r.status_code != 201:
        print(f"Remove failed with code {r.status_code}: {r.text}")
        exit(1)
    print(f"Successfully removed {len(ids)} documents")
    exit(0)  # no need to save
