from .checktoken import CheckToken
from .createtoken import CreateToken
from .takefile import UploadFile
from .prediction import PredictionHandler

HANDLERS = (CheckToken, CreateToken, UploadFile, PredictionHandler)
