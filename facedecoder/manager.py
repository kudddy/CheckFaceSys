from .encoder import get_encoder
from os.path import join
from time import sleep
# from app import CacheManager
import asyncio
import aiomcache

ENCODER_PATH = "facedecoder/temp/encoders"
IMAGE_PATH = "facedecoder/temp/image"
SLEEP_TIME = 2

# memcached = CacheManager()


# ловим сообщение что нужно обновлять из очередени что нужно обновлять

# в очереди по ключу будет сообщение насчет обновления данных(в значение будет идентификатор названия папки где лежит
# zip архив)

loop = asyncio.get_event_loop()

mc = aiomcache.Client("127.0.0.1", 11211, loop=loop)

async def start_pulling():
    get = True
    while True:
        # тут читаем из memcached на предмет обновления
        name = "8897ed22723843758becd25e20e57970"

        # memcached.cache.get(b"update")

        if get:
            get_encoder(join(IMAGE_PATH, name), join(ENCODER_PATH, name))
            get = False
            print("зашли и декодировали фото ")
            # положили в в memcached


        sleep(SLEEP_TIME)


async def set_test():
    print('тут')
    await mc.set(b"check_flag", b"8897ed22723843758becd25e20e57970")
    a = await mc.get(b"check_flag")
    print(a)

    print('йо')

loop.run_until_complete(set_test())
