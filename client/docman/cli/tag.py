class Tag:
    @classmethod
    def add_parser(cls, subparser):
        parser = subparser.add_parser(
            "tag", description="Adds or removes tags from document."
        )
        parser.add_argument("--clear", action="store_true", help="clear all tags")
        parser.add_argument(
            "--remove",
            nargs="*",
            metavar="tag",
            help="removes tags",
            required=False,
            default=[],
        )
        parser.add_argument(
            "--add",
            nargs="*",
            metavar="tag",
            help="adds tags",
            required=False,
            default=[],
        )
        parser.add_argument("tags", nargs="*", help="adds tags", default=[])
        parser.set_defaults(function=cls.run)

    @classmethod
    def run(cls, doc, tags=[], remove=[], add=[], clear=False, **kwargs):
        doctags = set(doc.tags)
        if clear:
            doctags.clear()
        for tag in remove:
            if tag in doctags:
                doctags.remove(tag)
        for tag in tags + add:
            doctags.add(tag.lower().replace(" ", "_"))
        doc.tags = sorted(list(doctags))
        doc.save()
        print(" ".join(doc.tags))
        return 0
