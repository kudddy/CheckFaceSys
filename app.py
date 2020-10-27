import logging

from types import AsyncGeneratorType, MappingProxyType
from typing import AsyncIterable, Mapping

from aiohttp import PAYLOAD_REGISTRY
from aiohttp.web_app import Application
from aiohttp_apispec import setup_aiohttp_apispec, validation_middleware

from handlers import HANDLERS
from middleware import error_middleware, handle_validation_error, check_token_middleware
from payloads import AsyncGenJSONListPayload, JsonPayload
from utils.pg import setup_pg

api_address = "0.0.0.0"
api_port = 8081

MEGABYTE = 1024 ** 2
MAX_REQUEST_SIZE = 70 * MEGABYTE

log = logging.getLogger(__name__)


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




