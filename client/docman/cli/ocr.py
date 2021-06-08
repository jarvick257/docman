def ocr(subparser):
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
    parser.set_defaults(function=_run)


def _ocr_worker(job_q, result_q):
    import pytesseract
    import re

    punct = "[.,!?;:\r\t\n\[\]\(\)]"

    while True:
        file, lang = job_q.get()
        if file is None:
            break
        txt = pytesseract.image_to_string(file, lang=lang)
        # clean stop characters
        txt = re.sub(punct, " ", txt)
        # clean whitespace
        txt = re.sub("\s+", " ", txt).strip()
        words = sorted(set(txt.split(" ")))
        result_q.put(words)


def _run(doc, args):
    import datetime as dt
    from multiprocessing import Process, Queue
    from progress.bar import Bar

    lang = args.lang or doc.config["DEFAULT"]["default_language"]
    text = set()
    result_q = Queue()
    job_q = Queue()
    workers = [
        Process(target=_ocr_worker, args=(job_q, result_q))
        for _ in range(min(args.max_jobs, len(doc.scans)))
    ]
    [worker.start() for worker in workers]
    print(min(args.max_jobs, len(doc.scans)))
    print(len(workers))
    [job_q.put((scan, lang)) for scan in doc.scans]
    [job_q.put((None, None)) for _ in workers]

    try:
        # bar = Bar(f"Analyzing {len(doc.scans)} documents", max=len(doc.scans))
        for i in range(len(doc.scans)):
            # bar.next()
            words = result_q.get()
            for word in words:
                text.add(word)
    except KeyboardInterrupt:
        [worker.terminate() for worker in workers]
        print("Caught keyboard interrupt. Stopping workers...")
    finally:
        # bar.finish()
        [worker.join() for worker in workers]

    print(f"{len(text)}")
    doc.ocr = " ".join(sorted(text))
    return doc, 0
