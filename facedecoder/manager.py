from .encoder import get_encoder, extract_zip
from os.path import join
from time import sleep
# from app import CacheManager
import asyncio
import aiomcache

ENCODER_PATH = "facedecoder/temp/encoders"
IMAGE_PATH = "facedecoder/temp/image"
ZIP_PATH = "facedecoder/temp/zip"
SLEEP_TIME = 2

# memcached = CacheManager()


# ловим сообщение что нужно обновлять из очередени что нужно обновлять

# в очереди по ключу будет сообщение насчет обновления данных(в значение будет идентификатор названия папки где лежит
# zip архив)

loop = asyncio.get_event_loop()

mc = aiomcache.Client("127.0.0.1", 11211, loop=loop)


async def start_pulling():
    # TODO добавить техничесую ифнормацию
    while True:
        # memcached.cache.get(b"update")
        name_model = await mc.get(b"update")
        if name_model != b"false":
            if name_model is not None:
                name_model = name_model.decode()
                extract_zip(join(ZIP_PATH, name_model), IMAGE_PATH)
                get_encoder(join(IMAGE_PATH, name_model), join(ENCODER_PATH, name_model))
                await mc.set(b"update", b"false")
                await mc.set(b"check_flag", name_model.encode())
                print("зашли и декодировали фото ")
            # положили в в memcached

        sleep(SLEEP_TIME)





async def set_test():
    print('тут')

    # a = await mc.get(b"check_flag")
    await mc.set(b"update", b"false")
    print("лолол")


loop.run_until_complete(start_pulling())
