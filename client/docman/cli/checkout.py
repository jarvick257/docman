class Checkout:
    @classmethod
    def add_parser(cls, subparser):
        parser = subparser.add_parser(
            "checkout",
            description="Loads documents from server into working directory.",
        )
        parser.add_argument("_id", metavar="id", help="document id")
        parser.add_argument(
            "--update",
            action="store_true",
            help="checkout in 'update' mode. This will only download meta data and no actual files.",
        )
        parser.set_defaults(function=cls.run)

    @classmethod
    def run(cls, doc, _id, update=False, **kwargs):
        import os
        import json
        import requests
        import urllib.request

        from docman import Document
        from .pull import Pull
        from .import_ import Import

        # don't overwrite existing document
        if doc.is_wip():
            print(
                "Refusing to checkout: Current working directory not empty.\n"
                "Push current document with 'docman push' or discard everything with "
                "'docman reset --hard'"
            )
            return 1

        # Load pdf/a
        Pull.run(doc, _id=_id, output=doc.wd, keep_id=True)

        # Load metadata
        Import.run(doc, [os.path.join(doc.wd, _id + ".pdf")])

        # Mark as update
        doc.mode = "update"
        doc._id = _id
        doc.save()

        return 0
