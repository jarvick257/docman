class Scan:
    @classmethod
    def add_parser(cls, subparser):
        parser = subparser.add_parser(
            "scan",
            description="""Adds new files to the current working state."""
            """ When scan is called after ocr or pdf, existing ocr and pdf data will be deleted.""",
        )
        parser.set_defaults(function=cls.run)

    @classmethod
    def run(cls, doc, **kwargs):
        import os
        from datetime import datetime
        import subprocess as sp

        timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
        output = os.path.join(doc.wd, f"{timestamp}.jpg")
        command_template = doc.config["INTEGRATION"]["scan"]
        cmd = command_template.replace("{file}", output)
        print(cmd)
        try:
            sp.check_call(cmd.split())
        except sp.CalledProcessError as e:
            print(f"{cmd} failed with return value {e.args[0]}!")
            return 1
        except FileNotFoundError as e:
            print(f"{cmd.split()[0]} doesn't exist!")
            return 1

        if doc.pdf is not None:
            doc.pdf = None
            print("Input files changed! Removed existing PDF")
        if doc.ocr is not None:
            doc.ocr = None
            print("Input files changed! Removed existing OCR")
        doc.input_files.append(output)
        doc.save()
        return 0
