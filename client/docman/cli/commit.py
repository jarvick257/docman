class Commit:
    @classmethod
    def add_parser(cls, subparser):
        # only needed for --help
        parser = subparser.add_parser(
            "commit", description="Combines inputs files into a PDF/A."
        )
        parser.add_argument(
            "--redo_ocr",
            action="store_true",
            help="Discard detected text and redo ocr",
        )
        parser.set_defaults(function=cls.run)

    @classmethod
    def run(cls, doc, redo_ocr=False, **kwargs):
        import os
        import subprocess as sp
        from pdfrw import PdfReader, PdfWriter
        from tzlocal import get_localzone

        if len(doc.input_files) > 1:
            # Convert/combine image files to pdf first
            print("Creating single pdf from input files")
            inputs = " ".join(doc.input_files)
            output = os.path.join(doc.wd, "combined.pdf")
            cmd = ["img2pdf", "--pagesize", "A4", "-o", output] + doc.input_files
            try:
                sp.check_call(cmd)
            except sp.CalledProcessError as e:
                print(f"{' '.join(cmd)} failed with return value {e.args[0]}!")
                return 1
            except:
                print(f"{' '.join(cmd)} failed!")
                return 1
            input_file = output
        elif len(doc.input_files) == 1 and doc.input_files[0].endswith(".pdf"):
            # pdf as input
            input_file = doc.input_files[0]
        else:
            print("Unsupported input!")
            print("Must have either multiple image files or a single pdf as input.")
            return 1

        print("Calling OcrMyPdf")

        output = os.path.join(doc.wd, "combined.pdf")
        cmd = [
            "ocrmypdf",
            "--title",
            doc.title,
            "--keywords",
            ":".join(doc.tags),
            "--output-type",
            "pdfa",
            input_file,
            output,
        ]
        if doc.ocr and not redo_ocr:
            cmd.append("--skip-text")
        else:
            doc.ocr = os.path.join(doc.wd, "ocr.txt")
            cmd += ["-l", "deu", "--sidecar", doc.ocr]
            if redo_ocr:
                cmd.append("--redo-ocr")

        try:
            sp.check_call(cmd)
        except:
            print(f"OcrMyPdf Failed!")
            return 1
        doc.pdf = output
        t = doc.date.replace(tzinfo=get_localzone())
        t = t.strftime("%Y%m%d%H%M%S%z")
        t = f"{t[:-2]}'{t[-2:]}"
        trailer = PdfReader(doc.pdf)
        trailer.Info.CreationDate = f"D:{t}"
        PdfWriter(doc.pdf, trailer=trailer).write()
        doc.save()
        return 0
