class Reset:
    @classmethod
    def add_parser(cls, subparser):
        parser = subparser.add_parser(
            "reset",
            description="Resets working state (by default, existing input files are kept)",
        )
        parser.add_argument(
            "--hard",
            action="store_true",
            help="delete all files, including input files",
        )
        parser.set_defaults(function=cls.run)

    @classmethod
    def run(cls, doc, hard=False, **kwargs):
        from datetime import date
        import glob
        import os
        from docman import Document

        doc = Document.load({})
        if not hard:
            doc.input_files = sorted(glob.glob(os.path.join(doc.wd, "*.jpg")))
        doc.save()
        return 0
