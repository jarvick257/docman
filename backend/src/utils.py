import re
import os
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
    collection = db["docman"]
    return collection


def archive():
    return os.environ.get("DOCMAN_ARCHIVE", "/data")


def db_lookup(tags=None, text=None, date_from=None, date_until=None, _id=None):
    collection = _connect_db()
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
    result = {str(result["_id"]): result for result in collection.find(query)}
    for post in result.values():
        post["_id"] = str(post["_id"])
        post["date"] = str(post["date"].date())
    print("Query:", query)
    return result


def db_add(post: dict, pdf, scans: list):
    # existing _id means replace doc -> delte and create new with given id
    if "_id" in post:
        post["_id"] = ObjectId(post["_id"])
        txt, code = db_delete(post["_id"])
        if code != 200:
            return txt, code

    # fromisoformat only available in python3.7
    # post["date"] = datetime.fromisoformat(post["date"])
    post["date"] = datetime.strptime(post["date"], "%Y-%m-%d")
    date_str = post["date"].strftime("%Y%m%d")

    # Save PDF
    pdf_file = f"{date_str}-{post['title']}.pdf"
    pdf_path = os.path.join(archive(), pdf_file)
    if os.path.isfile(pdf_path):
        return "Document already exists!", 409
    pdf.save(pdf_path)
    post["pdf"] = pdf_file

    # Save scans
    scan_path = os.path.join(archive(), ".scans")
    if not os.path.isdir(scan_path):
        os.mkdir(scan_path)
    post["scans"] = []
    for i, scan in enumerate(scans):
        fmt = "jpg" if "." not in scan.filename else scan.filename.split(".")[-1]
        scan_file = f"{date_str}-{post['title']}-{i:02d}.{fmt}"
        scan_path = os.path.join(scan_path, scan_file)
        if os.path.isfile(scan_path):
            return "Document already exists!", 409
        scan.save(scan_path)
        post["scans"].append(scan_file)

    # Register db
    try:
        collection = _connect_db()
        collection.insert_one(post)
    except:
        return "Failed to add document to database", 500
    return "OK", 201


def db_delete(_id: ObjectId):
    query = dict(_id=_id)
    try:
        collection = _connect_db()
    except:
        return "Failed to connect to database", 500
    doc = collection.find_one(query)
    if doc == {}:
        return f"No such document {_id}", 404
    # delete files
    os.remove(os.path.join(archive(), doc["pdf"]))
    for scan in doc["scans"]:
        os.remove(os.path.join(archive(), ".scans", scan))
    # delte db entry
    collection.delete_one(query)
    return "OK", 200


def _create_thumbnail(pdf_path: str, thumb_path: str):
    pdf = fitz.open(pdf_path)
    xref = pdf.getPageImageList(0)[0]
    image_data = pdf.extractImage(xref[0])
    size = (image_data["width"], image_data["height"])
    image = Image.open(io.BytesIO(image_data["image"]))
    image.thumbnail((400, 400), Image.ANTIALIAS)
    image.save(thumb_path)
    print(f"Created {thumb_path} with size {image.size}")


def get_thumbnail(thumb_name: str):
    thumb_dir = os.path.join(archive(), ".thumbs")
    thumb_path = os.path.join(thumb_dir, thumb_name)
    if not os.path.isfile(thumb_path):
        print(f"{thumb_path} doesn't exist")
        if not os.path.isdir(thumb_dir):
            os.mkdir(thumb_dir)
        pdf_name = thumb_name.rsplit(".", 1)[0] + ".pdf"
        print(f"Creating {thumb_name} from {pdf_name}")
        _create_thumbnail(os.path.join(archive(), pdf_name), thumb_path)
    return thumb_dir, thumb_name
