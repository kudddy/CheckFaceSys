import logging

from .encoder import get_encoder, extract_zip
from os.path import join

ENCODER_PATH = "facedecoder/temp/encoders"
IMAGE_PATH = "facedecoder/temp/image"
ZIP_PATH = "facedecoder/temp/zip"
SLEEP_TIME = 2
logging.basicConfig(level=logging.DEBUG)
log = logging.getLogger(__name__)

log.setLevel(logging.DEBUG)


# ловим сообщение что нужно обновлять из очередени что нужно обновлять

# в очереди по ключу будет сообщение насчет обновления данных(в значение будет идентификатор названия папки где лежит
# zip архив)

def run_model_updater(name_model: tuple):
    log.debug("Start create model - %r", name_model[1])
    log.debug("Extract zip - %r", name_model[1])

    extract_zip(join(ZIP_PATH, name_model[1]), IMAGE_PATH)

    log.debug("Done extract zip - %r", name_model[1])
    log.debug("create encoders - %r", name_model[1])

    result = get_encoder(join(IMAGE_PATH, name_model[1]), join(ENCODER_PATH, name_model[1]))

    log.debug("done encoders - %r", name_model[1])
    return result
