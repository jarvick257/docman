def _ocr_worker(job_q, result_q):
    import pytesseract

    while True:
        file, lang = job_q.get()
        if file is None:
            break
        txt = pytesseract.image_to_string(file, timeout=300, lang=lang)
        txt = txt.replace("\n", " ")
        txt = txt.replace(".", " ")
        txt = txt.replace("!", " ")
        txt = txt.replace("?", " ")
        txt = txt.replace(",", " ")
        txt = txt.replace(";", " ")
        txt = txt.replace(":", " ")
        words = set(txt.split(" "))
        result_q.put(words)


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
        help="max number of parallel ocr jobs. DEFAULT: %(default)s",
        default=4,
    )
    parser.set_defaults(function=_run)


def _run(args):
    import datetime as dt
    from multiprocessing import Process, Queue
    from progress.bar import Bar
    import pytesseract
    from docman import Document
    from docman.utils import get_config

    if args.lang is None:
        config = get_config()
        args.lang = config["DEFAULT"]["default_language"]
    doc = Document.load()
    text = set()
    result_q = Queue()
    job_q = Queue()
    workers = [
        Process(target=_ocr_worker, args=(job_q, result_q))
        for _ in range(min(args.max_jobs, len(doc.scans)))
    ]
    [worker.start() for worker in workers]
    [job_q.put((scan, args.lang)) for scan in doc.scans]
    [job_q.put((None, None)) for _ in range(len(workers))]

    bar = Bar(f"Analyzing {len(doc.scans)} documents", max=len(doc.scans))
    for i in range(len(doc.scans)):
        bar.next()
        words = result_q.get()
        for word in words:
            text.add(word.strip())
    bar.finish()
    [worker.join() for worker in workers]

    print(f"Found {len(text)} unique words")
    doc.ocr = " ".join(text)
    doc.save()
