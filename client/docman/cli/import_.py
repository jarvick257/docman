class Import:
    @classmethod
    def add_parser(cls, subparser):
        parser = subparser.add_parser(
            "import",
            description="Imports one or more PDF, PDF/A or image files into working state",
        )
        parser.add_argument(
            "paths",
            nargs="+",
            help="Path to pdf or image file",
        )
        parser.set_defaults(function=cls.run)

    @classmethod
    def run(cls, doc, paths: list, **kwargs):
        if doc.is_wip():
            print(
                "Refusing to import: Current working directory not empty.\n"
                "Push current document with 'docman push' or discard everything with "
                "'docman reset --hard'"
            )
            return 1

        for path in paths:
            if path.endswith(".pdf"):
                cls.import_pdf(doc, path)
            elif path.split(".")[-1].lower() in ["jpg", "jpeg", "png"]:
                cls.import_image(doc, path)
            else:
                print("Unsupported file format: ", path)
        doc.save()

    @classmethod
    def import_pdf(cls, doc, path):
        import os
        import fitz
        import shutil
        from datetime import datetime

        pdf = fitz.open(path)
        meta = pdf.metadata
        doc.title = meta.get("title", None)
        doc.tags = [t for t in meta.get("keywords", "").split(":") if t != ""]
        if "creationDate" in meta:
            date = meta["creationDate"].split(":")[-1]
            date = date.replace("'", "")
            try:
                date = datetime.strptime(date, "%Y%m%d%H%M%S%z")
            except ValueError:
                date = datetime.strptime(date, "%Y%m%d%H%M%S")
            doc.date = date
        text = ""
        for i in range(pdf.pageCount):
            text += pdf.loadPage(i).getText("text")
        text = text.replace("\n", " ").replace("  ", " ").strip()
        if text != "":
            ocr = os.path.join(doc.wd, "ocr.txt")
            with open(ocr, "w") as fp:
                fp.write(text)
            doc.ocr = ocr
        target = os.path.join(doc.wd, os.path.basename(path))
        if path != target:
            shutil.copy(path, target)
        doc.input_files.append(target)

    @classmethod
    def import_image(cls, doc, path):
        import os
        import shutil

        target = os.path.join(doc.wd, os.path.basename(path))
        if path != target:
            shutil.copy(path, target)
        doc.input_files.append(target)
