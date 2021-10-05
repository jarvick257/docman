class Import:
    @classmethod
    def add_parser(cls, subparser):
        parser = subparser.add_parser(
            "import",
            description="Imports an existing PDF/A file into working state",
        )
        parser.add_argument(
            "path",
            metavar="pdf",
            help="Path to PDF/A File",
        )
        parser.set_defaults(function=cls.run)

    @classmethod
    def run(cls, doc, path, **kwargs):
        import os
        from datetime import datetime
        from pdfrw import PdfReader
        from subprocess import check_call
        import shutil

        if doc.is_wip():
            print(
                "Refusing to import: Current working directory not empty.\n"
                "Push current document with 'docman push' or discard everything with "
                "'docman reset --hard'"
            )
            return 1

        pdf = PdfReader(path)
        doc.title = pdf.Info.Title.decode().lower().replace(" ", "_")
        doc.tags = sorted(list(set(pdf.Info.Keywords.decode().split(":"))))
        date = pdf.Info.CreationDate.decode().split(":")[-1]
        date = date.replace("'", "")
        date = datetime.strptime(date, "%Y%m%d%H%M%S%z")
        doc.date = date
        try:
            doc.ocr = os.path.join(doc.wd, "ocr.txt")
            check_call(["pdftotext", path, doc.ocr])
        except:
            doc.ocr = None
        target = os.path.join(doc.wd, os.path.basename(path))
        if path != target:
            shutil.copy(path, target)
        doc.pdf = None
        doc.input_files = [target]
        doc.save()

        return 0
