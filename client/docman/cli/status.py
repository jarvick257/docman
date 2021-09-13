class Status:
    @classmethod
    def add_parser(cls, subparser):
        parser = subparser.add_parser(
            "status", description="Shows current working state"
        )
        parser.add_argument("--json", action="store_true", help="show output as json")
        parser.add_argument(
            "--full_ocr", action="store_true", help="show full ocr output"
        )
        parser.set_defaults(function=cls.run)

    @classmethod
    def run(cls, doc, json=False, full_ocr=False, **kwargs):
        import os

        if full_ocr:
            ocr_str = doc.ocr
        else:
            ocr_words = 0 if doc.ocr is None else len(doc.ocr.split(" "))
            ocr_str = f"{ocr_words} words"

        if json:
            import json

            # dump dict and we're done
            d = doc.to_dict()
            d["ocr"] = ocr_str
            print(json.dumps(d, indent=2))
            return 0

        if doc.mode == "add":
            mode = doc.mode
        else:
            mode = f"{doc.mode} {doc._id}"
        print(f"Mode:   {mode}")
        print(f"Title:  {doc.title}")
        print(f"Date:   {doc.date.date()}")
        print(f"Tags:   {'None' if doc.tags == [] else ' '.join(doc.tags)}")
        print(f"Inputs: {len(doc.input_files)}")
        for i in doc.input_files:
            print(f"    - {os.path.basename(i)}")
        print(f"Pdf:    {'Yes' if doc.pdf else 'No'}")
        return 0
