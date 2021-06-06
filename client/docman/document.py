import os
import datetime as dt
import json
import glob

from docman.utils import get_config


class Document:
    def __init__(self):
        self.scans = []
        self.tags = []
        self.mode = None
        self._id = None
        self.ocr = None
        self.pdf = None
        self.date = None
        self.post = None
        self.title = None
        self.config = None
        self.wd = None

    @classmethod
    def load(cls, meta=None):
        config = get_config()
        wd = config["DEFAULT"]["working_dir"]
        meta_path = os.path.join(wd, "meta.json")
        if meta is None:
            try:
                with open(meta_path) as fp:
                    meta = json.load(fp)
            except (FileNotFoundError, NotADirectoryError):
                meta = {}
        doc = Document()
        doc._id = meta.get("_id", None)
        doc.scans = meta.get("scans", [])
        doc.tags = meta.get("tags", [])
        doc.ocr = meta.get("ocr", None)
        doc.pdf = meta.get("pdf", None)
        doc.title = meta.get("title", None)
        doc.date = meta.get("date", str(dt.date.today()))
        doc.mode = meta.get("mode", "add")
        doc.wd = wd
        doc.config = config
        doc.path = meta_path
        return doc

    @property
    def server_url(self):
        return (
            f"http://{self.config['SERVER']['address']}:{self.config['SERVER']['port']}"
        )

    def is_wip(self):
        return not (
            self.scans == []
            and self.tags == []
            and self.ocr is None
            and self.pdf is None
            and self.title is None
        )

    def cleanup(self):
        for f in glob.glob(os.path.join(self.wd, "*")):
            if not os.path.isfile(f):
                continue
            if f not in self.scans and f != self.pdf and f != self.path:
                os.remove(f)

    def save(self):
        meta = self.to_dict()
        if not os.path.isdir(self.wd):
            os.makedirs(self.wd)
        with open(self.path, "w") as fp:
            json.dump(meta, fp)

    def to_dict(self):
        return dict(
            mode=self.mode,
            _id=self._id,
            scans=self.scans,
            tags=self.tags,
            ocr=self.ocr,
            pdf=self.pdf,
            date=self.date,
            title=self.title,
        )
