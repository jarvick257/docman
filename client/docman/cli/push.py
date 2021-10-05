class Push:
    @classmethod
    def add_parser(cls, subparser):
        parser = subparser.add_parser(
            "push",
            description="""Pushes the current working state to the docman server and resets. """,
        )
        parser.set_defaults(function=cls.run)

    @classmethod
    def run(cls, doc, **kwargs):
        import os
        import requests
        import json

        from .reset import Reset

        # Check for if ready to be pushed
        if not doc.is_complete():
            print("Document is not ready to be pushed!")
            print("For adding, you need tags, a title, a pdf, a date and ocr")
            print("For updating, you need tags, a title, a date, ocr and an id")
            return 1

        # Prepare post
        url = doc.server_url
        if doc.mode == "update":
            url += f"/update/{doc._id}"
        elif doc.mode == "add":
            url += "/add"
        files = [("pdf", open(doc.pdf, "rb"))]
        try:
            r = requests.post(url, files=files)
        except:
            print(f"Failed to connect to server!")
            return 1

        if r.status_code == 201:
            # need an object with "hard" property set to True
            print("Push successful")
            return Reset.run(doc, hard=True)

        print(f"Push failed with code {r.status_code}: {r.text}")
        return 1
