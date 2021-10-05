from .checkout import Checkout
from .commit import Commit
from .config import Config
from .date import Date
from .import_ import Import
from .mode import Mode
from .ocr import Ocr
from .preview import Preview
from .pull import Pull
from .push import Push
from .query import Query
from .reset import Reset
from .rm import Rm
from .scan import Scan
from .status import Status
from .tag import Tag
from .title import Title

COMMANDS = [
    Checkout,
    Commit,
    Config,
    Date,
    Import,
    Mode,
    Ocr,
    Preview,
    Pull,
    Push,
    Query,
    Reset,
    Rm,
    Scan,
    Status,
    Tag,
    Title,
]

DEFAULT = Status
