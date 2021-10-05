class Title:
    @classmethod
    def add_parser(cls, subparser):
        parser = subparser.add_parser("title", description="Sets the document title.")
        parser.add_argument(
            "--clear",
            action="store_true",
            help="clears the title without setting a new one",
        )
        parser.add_argument("title", nargs="*", help="title of the document")
        parser.set_defaults(function=cls.run)

    @classmethod
    def run(cls, doc, title=[], clear=False, **kwargs):
        if clear:
            doc.title = None
            doc.save()
        elif title != []:
            # When title is passed as multiple args
            title = "_".join(title)
            # When title is passed as single arg (eg in quotes)
            title = title.replace(" ", "_")
            doc.title = title
            doc.save()
        print("" if doc.title is None else doc.title)
        return 0
