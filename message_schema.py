"""
Модуль содержит схемы для валидации данных в запросах и ответах.

Схемы Валидации ответов *ResponseSchema используется только при тестировании,
чтоды убедиться что обработчик возвращает данные в корректном формате.
"""

from datetime import date

from marshmallow import Schema
from marshmallow.fields import Str


class CheckTokenReq(Schema):
    token_status = Str()
