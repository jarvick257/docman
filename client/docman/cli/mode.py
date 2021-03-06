class Mode:
    @classmethod
    def add_parser(cls, subparser):
        parser = subparser.add_parser(
            "mode",
            description="Change the edit mode. "
            "You can think of it as 'what are your intentions when pushing to the server?'. "
            "Do you want to 'add' a new document or "
            "Do you want to 'update' an existing document?",
        )
        parser.add_argument(
            "mode",
            choices=["add", "update"],
            help="edit mode",
        )
        parser.add_argument(
            "--id",
            required=False,
            help="document id",
        )
        parser.set_defaults(function=cls.run)

    @classmethod
    def run(cls, doc, mode: str, _id=None, **kwargs):
        doc.mode = mode

        if _id:
            doc._id = _id

        if doc.mode == "add" and doc._id is not None:
            # add with id is not supported but won't throw error
            # also id is kept so when changing back to another mode won't require an id anymore
            print(
                "Warning: Adding a document for a given ID is not supported. "
                "The specified id will be ignored."
            )
        elif doc.mode != "add" and doc._id is None:
            # change without id doesn't work
            print(
                "Error: When choosing a mode other than 'add', an existing document id is required!"
            )
            return 1
        doc.save()
        print(doc.mode)
        return 0
