import re
import os
from loguru import logger
from datetime import datetime
from pymongo import MongoClient
from bson.objectid import ObjectId
import fitz
import io
from PIL import Image


def _connect_db():
    server = os.environ.get("DOCMAN_DB", "127.0.0.1")
    user = os.environ.get("DOCMAN_USER", None)
    passwd = os.environ.get("DOCMAN_PASS", None)
    if user and passwd:
        client = MongoClient(f"mongodb://{user}:{passwd}@{server}")
    else:
        client = MongoClient(f"mongodb://{server}")
    db = client["docman"]
    return db["docman"]


def archive(*args):
    path = [os.environ.get("DOCMAN_ARCHIVE", "/data")] + list(args)
    return os.path.join(*path)


def db_lookup(tags=None, text=None, date_from=None, date_until=None, _id=None):
    db = _connect_db()
    query = {}
    if _id:
        query["_id"] = ObjectId(_id)
    if tags:
        query["tags"] = {"$all": tags}
    if date_from:
        if "date" not in query:
            query["date"] = {}
        if isinstance(date_from, str):
            date_from = datetime.strptime(date_from, "%Y-%m-%d")
        query["date"]["$gte"] = date_from
    if date_until:
        if "date" not in query:
            query["date"] = {}
        if isinstance(date_until, str):
            date_until = datetime.strptime(date_until, "%Y-%m-%d")
        query["date"]["$lte"] = date_until
    if text:
        query["ocr"] = {"$regex": re.compile(".*" + text + ".*", re.IGNORECASE)}
    result = {str(result["_id"]): result for result in db.find(query)}
    for post in result.values():
        post["_id"] = str(post["_id"])
        post["date"] = str(post["date"].date())
    logger.debug(f"Query: {query}")
    return result


def db_add(
    filename: str, title: str, date: datetime, tags: list, text: str, _id: str = None
):
    logger.info(f"Adding new document: {title}")
    post = {
        "pdf": filename,
        "title": title,
        "date": date,
        "tags": tags,
        "ocr": text,
    }
    if _id:
        post["_id"] = ObjectId(_id)

    try:
        db = _connect_db()
        db.insert_one(post)
    except:
        return "Failed to add document to database", 500
    return "OK", 201


def db_delete(_id_str: str):
    logger.info(f"Deleting {_id_str}")
    _id = ObjectId(_id_str)
    query = dict(_id=_id)
    try:
        db = _connect_db()
    except:
        logger.error("Failed to connect to database")
        return "Failed to connect to database", 500
    doc = db.find_one(query)
    if doc is None or doc == {}:
        logger.error("Document doesn't exist")
        return f"No such document {_id}", 404
    # delete files
    os.remove(archive(doc["pdf"]))
    # delte db entry
    db.delete_one(query)
    return "OK", 201


def db_update(post: dict):
    _id = post["_id"]
    id_query = dict(_id=ObjectId(post["_id"]))
    del post["_id"]
    post["date"] = datetime.strptime(post["date"], "%Y-%m-%d")
    logger.info(f"Updating {_id}")
    try:
        db = _connect_db()
    except:
        logger.error("Failed to connect to database")
        return "Failed to connect to database", 500
    doc = db.find_one(id_query)
    if doc is None or doc == {}:
        logger.error("Document doesn't exist")
        return f"No such document {_id}", 404
    # update doc
    # This step is necessary so that we can change some attributes of the document
    # while keeping others untouched
    for k, v in post.items():
        if k not in doc:
            return f"Unknown attribute: {k}", 400
        doc[k] = v
    # replace in db with updated doc
    db.replace_one(id_query, doc)
    return "OK", 201


def _create_thumbnail(pdf_path: str, thumb_path: str):
    pdf = fitz.open(pdf_path)
    xref = pdf.getPageImageList(0)[0]
    image_data = pdf.extractImage(xref[0])
    size = (image_data["width"], image_data["height"])
    image = Image.open(io.BytesIO(image_data["image"]))
    image.thumbnail((400, 400), Image.ANTIALIAS)
    image.save(thumb_path)
    logger.debug(f"Created {thumb_path} with size {image.size}")


def get_thumbnail(thumb_name: str):
    thumb_dir = archive(".thumbs")
    thumb_path = os.path.join(thumb_dir, thumb_name)
    if not os.path.isfile(thumb_path):
        logger.debug(f"{thumb_path} doesn't exist")
        if not os.path.isdir(thumb_dir):
            os.mkdir(thumb_dir)
        pdf_name = thumb_name.rsplit(".", 1)[0] + ".pdf"
        logger.debug(f"Creating {thumb_name} from {pdf_name}")
        _create_thumbnail(archive(pdf_name), thumb_path)
    return thumb_dir, thumb_name
