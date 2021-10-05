class Preview:
    @classmethod
    def add_parser(cls, subparser):
        parser = subparser.add_parser(
            "preview",
            description="Previews scans or PDFs from the current working state.",
        )
        parser.add_argument("--inputs", action="store_true", help="preview input files")
        parser.add_argument("--pdf", action="store_true", help="preview pdf")
        parser.set_defaults(function=cls.run)

    @classmethod
    def run(cls, doc, inputs=False, pdf=False, **kwargs):
        import os

        auto = not (pdf or inputs)
        if (pdf or auto) and doc.pdf is not None:
            print("Previewing pdf")
            os.system(f"xdg-open {doc.pdf}")
        elif (inputs or (auto and not doc.pdf)) and doc.input_files != []:
            print("Previewing scans")
            files = " ".join(doc.input_files)
            os.system(f"xdg-open {files}")
        else:
            print("Nothing to preview")
        return 0
