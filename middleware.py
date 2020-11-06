import logging
from http import HTTPStatus
from typing import Mapping, Optional

from aiohttp.web_exceptions import (
    HTTPBadRequest, HTTPException, HTTPInternalServerError, HTTPForbidden
)
from aiohttp.web_response import Response
from aiohttp.web_middlewares import middleware
from aiohttp.web_request import Request
from marshmallow import ValidationError

from payloads import JsonPayload

from db.schema import all_tokens
from handlers.query import CHECK_TOKEN

log = logging.getLogger(__name__)


def format_http_error(http_error_cls, message: Optional[str] = None,
                      fields: Optional[Mapping] = None) -> HTTPException:
    """
    Форматирует ошибку в виде HTTP исключения
    """
    status = HTTPStatus(http_error_cls.status_code)
    error = {
        'code': status.name.lower(),
        'message': message or status.description
    }

    if fields:
        error['fields'] = fields

    return http_error_cls(body={'error': error})


def handle_validation_error(error: ValidationError, *_):
    """
    Представляет ошибку валидации данных в виде HTTP ответа.
    """
    raise format_http_error(HTTPBadRequest, 'Request validation has failed',
                            error.messages)


@middleware
async def error_middleware(request: Request, handler):
    print(request)
    try:
        print(handler)
        return await handler(request)
    except HTTPException as err:
        print('мы тут')
        # Исключения которые представляют из себя HTTP ответ, были брошены
        # осознанно для отображения клиенту.

        # Текстовые исключения (или исключения без информации) форматируем
        # в JSON
        if not isinstance(err.body, JsonPayload):
            err = format_http_error(err.__class__, err.text)

        raise err

    except ValidationError as err:
        print('а теперь утт')
        # Ошибки валидации, брошенные в обработчиках
        raise handle_validation_error(err)

    except Exception as e:
        print(e)
        # Все остальные исключения не могут быть отображены клиенту в виде
        # HTTP ответа и могут случайно раскрыть внутреннюю информацию.
        log.exception('Unhandled exception')
        raise format_http_error(HTTPInternalServerError)


@middleware
async def check_token_middleware(request: Request, handler):
    # TODO очень грязно, возможно стоит избавиться
    if request.path in ("/{token}/token_status", "/{token}/check_similarity/{encoder_uid}/",
                        "/{token}/upload_file"):

        # TODO возможно стоит использовать aiohttp_security
        pg = request.app['pg']

        request.match_info.get('token')
        query = CHECK_TOKEN.where(all_tokens.c.token == request.match_info.get('token'))

        result = await pg.fetch(query)

        if len(result) > 0:
            return await handler(request)
        else:
            raise HTTPForbidden
    else:
        return await handler(request)
