class Rm:
    @classmethod
    def add_parser(cls, subparser):
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
        parser.set_defaults(function=cls.run)

    @classmethod
    def run(cls, doc, ids: list, noconfirm=False, **kwargs):
        import os
        import json
        import requests

        url = doc.server_url

        # Check ids
        existing_ids = []
        for _id in sorted(set(ids)):  # sorted only needed for unittests
            # get document info
            response = requests.get(f"{url}/query", json=dict(id=_id))
            if response.status_code != 200 or response.json() == {}:
                print(f"Warning: No document found for id {_id}")
                continue
            meta = response.json()[_id]
            existing_ids.append(_id)

        if len(existing_ids) == 0:
            print("Nothing to delete.")
            return 0

        # Ask for confirmation
        pl = lambda x: "s" if x != 1 else ""
        print(f"You are about to delete {len(ids)} document{pl(len(existing_ids))}.")
        if not noconfirm:
            r = input("If you wish to continue, please type yes: ")
            if r.lower() != "yes":
                print("Aborting...")
                return 1

        # Delete
        r = requests.post(f"{url}/remove", json=dict(ids=existing_ids))
        if r.status_code != 201:
            print(f"Remove failed with code {r.status_code}: {r.text}")
            return 1
        print(
            f"Successfully removed {len(existing_ids)} document{pl(len(existing_ids))}"
        )
        return 0
