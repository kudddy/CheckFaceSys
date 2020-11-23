import logging
from os import listdir
from os.path import join

from types import AsyncGeneratorType, MappingProxyType
from typing import AsyncIterable, Mapping

from aiohttp import PAYLOAD_REGISTRY
from aiohttp.web_app import Application
from aiohttp_apispec import setup_aiohttp_apispec, validation_middleware
from concurrent.futures.process import ProcessPoolExecutor

import aiomcache
import asyncio

from handlers import HANDLERS
from middleware import error_middleware, handle_validation_error, check_token_middleware
from payloads import AsyncGenJSONListPayload, JsonPayload
from utils.pg import setup_pg
from helper import Pickler, check_folder_in_path

from facedecoder.manager import run_model_updater
from db.schema import done_encoders

ENCODERS_PATH = 'facedecoder/temp/encoders'
api_address = "0.0.0.0"
api_port = 8081

MEGABYTE = 1024 ** 2
MAX_REQUEST_SIZE = 70 * MEGABYTE

logging.basicConfig(level=logging.DEBUG)
log = logging.getLogger(__name__)

log.setLevel(logging.DEBUG)

pickler = Pickler()

check_folder_in_path()


class CacheManager:
    def __init__(self):
        self.cache = aiomcache.Client("127.0.0.1", 11211, pool_size=2)

    async def get(self, key):
        return await asyncio.wait_for(self.cache.get(key), 0.1)

    async def set(self, key, value):
        return await asyncio.wait_for(self.cache.set(key, value), 0.1)


class EncoderManager:
    def __init__(self):
        self.pickler = Pickler()
        self.encoders = {}
        self.get_all_encoder_by_hdd_sync()

    def get_all_encoder_by_hdd_sync(self):
        for encoder in listdir(ENCODERS_PATH):
            try:
                self.encoders[encoder] = self.pickler.sync_pickler(join(ENCODERS_PATH, encoder))
            except:
                pass

    async def get_all_encoder_by_hdd_async(self):
        # TODO проверить работоспособность этого метода
        for encoder in listdir(ENCODERS_PATH):
            try:
                self.encoders[encoder] = await self.pickler.async_pickler(join(ENCODERS_PATH, encoder))
            except:
                pass

    def get_encoder_by_uid(self, uid: str) -> dict:
        return self.encoders[uid]

    def update_encoder_by_uid(self, uid: str, encoder: dict) -> None:
        self.encoders[uid] = encoder

    def check_key(self, uid: str) -> bool:
        if uid in self.encoders:
            return True
        else:
            return False


async def task_for_executor(app, tech_info_about_model: tuple):
    token, model_uid = tech_info_about_model
    loop = asyncio.get_event_loop()
    # TODO добавить проверку на успешное обновление
    result = await loop.run_in_executor(
        app.process_pool,
        run_model_updater, tech_info_about_model
    )
    # пишем в базу что апдейт прошел успешно или нет
    # TODO добавить поле с успешной записью
    if result['status']:
        # обновляем енкодер только для одной копии приложений.
        app['encoders'].update_encoder_by_uid(
            model_uid, result
        )
        query = done_encoders.insert().values(tech_info_about_model)
        await app['pg'].fetch(query)
        log.debug('Job id - %r status: %r', model_uid, True)
    else:
        log.debug('Job id - %r status: %r', model_uid, False)


async def input_queue_listener(app):
    while True:
        name_model = await app.input_queue.get()
        app.input_queue.task_done()
        loop = asyncio.get_event_loop()
        loop.create_task(task_for_executor(app, name_model))


async def startup(app):
    input_queue = asyncio.Queue()
    app.process_pool = ProcessPoolExecutor(3)
    app.input_queue = input_queue
    loop = asyncio.get_event_loop()
    loop.create_task(
        input_queue_listener(app)
    )


async def shutdown(app):
    app.listen_task.cancel()
    app.process_pool.shutdown()


def create_app() -> Application:
    """
    Создает экземпляр приложения, готового к запуску
    """
    # TODO добавить middlewares для вадидации полей сообщений
    app = Application(
        client_max_size=MAX_REQUEST_SIZE,
        middlewares=[check_token_middleware]
    )
    app.cleanup_ctx.append(setup_pg)

    app.on_startup.append(startup)
    app.on_shutdown.append(shutdown)

    # регестрируем менеджер кеша
    app['cache'] = CacheManager()
    app['encoders'] = EncoderManager()

    # Регистрация обработчика
    for handler in HANDLERS:
        log.debug('Registering handler %r as %r', handler, handler.URL_PATH)
        app.router.add_route('*', handler.URL_PATH, handler)

    setup_aiohttp_apispec(app=app, title="GROUP BY FACE API", swagger_path='/')

    # Автоматическая сериализация в json данных в HTTP ответах
    PAYLOAD_REGISTRY.register(AsyncGenJSONListPayload,
                              (AsyncGeneratorType, AsyncIterable))
    PAYLOAD_REGISTRY.register(JsonPayload, (Mapping, MappingProxyType))
    return app
