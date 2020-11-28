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

def run_model_updater(tech_info_about_model: tuple):

    token, model_uid = tech_info_about_model
    log.debug("Start create model - %r", model_uid)
    log.debug("Extract zip - %r", model_uid)

    # извлекаем содержимое архива в папку
    status: bool = extract_zip(join(ZIP_PATH, model_uid), IMAGE_PATH)
    if status:
        log.debug("Done extract zip - %r", model_uid)
        log.debug("create encoders - %r", model_uid)

        result: dict = get_encoder(join(IMAGE_PATH, model_uid), join(ENCODER_PATH, model_uid))

        log.debug("done encoders - %r", model_uid)
        return result
    else:
        return {"faces_encoders": [], "faces_mapping": [], "status": status}
