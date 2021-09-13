def _ocr_worker(job_q, result_q):
    import pytesseract
    import re

    punct = r"[.,!?;:\r\t\n\[\]\(\)]"

    while True:
        file, lang = job_q.get()
        if file is None:
            break
        txt = pytesseract.image_to_string(file, lang=lang)
        # clean stop characters
        txt = re.sub(punct, " ", txt)
        # clean whitespace
        txt = re.sub(r"\s+", " ", txt).strip()
        words = sorted(set(txt.split(" ")))
        result_q.put(words)


class Ocr:
    @classmethod
    def add_parser(cls, subparser):
        parser = subparser.add_parser(
            "ocr",
            description="""Extracts text from scans (Optical Character Recognition)."""
            """ The extracted text is not meant for being read directly but rather as something that can be searched in."""
            """ As a consequence, word duplicates will be removed and words may be out of order.""",
        )
        parser.add_argument(
            "--lang",
            metavar="lan",
            help="override config language (run tesseract --list-lan for a list of available options)",
            required=False,
        )
        parser.add_argument(
            "--max_jobs",
            type=int,
            metavar="N",
            help="max number of parallel ocr jobs (default: %(default)s)",
            default=4,
        )
        parser.set_defaults(function=cls.run)

    @classmethod
    def run(doc, lang=None, max_jobs=4):
        import datetime as dt
        from multiprocessing import Process, Queue

        lang = lang or doc.config["DEFAULT"]["default_language"]
        text = set()
        result_q = Queue()
        job_q = Queue()
        workers = [
            Process(target=_ocr_worker, args=(job_q, result_q))
            for _ in range(min(max_jobs, len(doc.scans)))
        ]
        [worker.start() for worker in workers]
        print(min(max_jobs, len(doc.scans)))
        print(len(workers))
        [job_q.put((scan, lang)) for scan in doc.scans]
        [job_q.put((None, None)) for _ in workers]

        try:
            N = len(doc.scans)
            for i in range(len(doc.scans)):
                print(f"{i+1}/N", end="\r")
                words = result_q.get()
                for word in words:
                    text.add(word)
        except KeyboardInterrupt:
            [worker.terminate() for worker in workers]
            print("Caught keyboard interrupt. Stopping workers...")
        finally:
            [worker.join() for worker in workers]

        print(f"{len(text)}" + " " * 10)
        doc.ocr = " ".join(sorted(text))
        return doc, 0
