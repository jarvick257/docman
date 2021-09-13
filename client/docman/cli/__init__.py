from .status import Status
from .scan import Scan
from .title import Title
from .pdf import Pdf
from .preview import Preview
from .config import Config
from .tag import Tag
from .reset import Reset
from .date import Date
from .ocr import Ocr
from .push import Push
from .query import Query
from .checkout import Checkout
from .pull import Pull
from .rm import Rm
from .mode import Mode

COMMANDS = [
    Status,
    Scan,
    Title,
    Pdf,
    Preview,
    Config,
    Tag,
    Reset,
    Date,
    Ocr,
    Push,
    Query,
    Checkout,
    Pull,
    Rm,
    Mode,
]

DEFAULT = Status
