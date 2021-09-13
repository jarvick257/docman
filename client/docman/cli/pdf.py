class Pdf:
    @classmethod
    def add_parser(cls, subparser):
        # only needed for --help
        parser = subparser.add_parser(
            "pdf", description="Combines inputs files into a PDFa."
        )
        parser.set_defaults(function=cls.run)

    @classmethod
    def run(cls, doc, **kwargs):
        import os
        import subprocess as sp
        from pdfrw import PdfReader, PdfWriter
        from tzlocal import get_localzone

        if len(doc.input_files) == 0:
            print("No input files!")
            return None, 1
        elif len(doc.input_files) > 1 or not doc.input_files[0].endswith(".pdf"):
            # Convert/combine input files to pdf first
            print("Create single pdf from input files")
            inputs = " ".join(doc.input_files)
            output = os.path.join(doc.wd, "combined.pdf")
            cmd = ["img2pdf", "--pagesize", "A4", "-o", output] + doc.input_files
            try:
                sp.check_call(cmd)
            except sp.CalledProcessError as e:
                print(f"{' '.join(cmd)} failed with return value {e.args[0]}!")
                return None, 1
            except:
                print(f"{' '.join(cmd)} failed!")
                return None, 1
            input_file = output
        else:
            input_file = doc.input_files[0]

        print("Calling OcrMyPdf")

        output = os.path.join(doc.wd, "combined.pdfa")
        ocr = os.path.join(doc.wd, "ocr.txt")
        cmd = [
            "ocrmypdf",
            "-l",
            "deu",
            "--title",
            doc.title,
            "--keywords",
            ":".join(doc.tags),
            "--sidecar",
            ocr,
            "--output-type",
            "pdfa",
            input_file,
            output,
        ]
        try:
            sp.check_call(cmd)
        except:
            print(f"OcrMyPdf Failed!")
            return None, 1
        doc.pdf = output
        t = doc.date.replace(tzinfo=get_localzone())
        t = t.strftime("%Y%m%d%H%M%S%z")
        t = f"{t[:-2]}'{t[-2:]}"
        trailer = PdfReader(doc.pdf)
        trailer.Info.CreationDate = f"D:{t}"
        PdfWriter(doc.pdf, trailer=trailer).write()
        doc.save()
        return 0
