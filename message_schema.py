"""
Модуль содержит схемы для валидации данных в запросах и ответах.

Схемы Валидации ответов *ResponseSchema используется только при тестировании,
чтоды убедиться что обработчик возвращает данные в корректном формате.
"""

from marshmallow import Schema
from marshmallow.fields import Str, Nested, List, Bool


class NameModelResp(Schema):
    MODEL_UID = Str()


class CheckTokenResp(Schema):
    MESSAGE_NAME = Str()
    TOKEN_STATUS = Bool()
    NAME_MODELS = List(Nested(NameModelResp))


class GetTokenPayload(Schema):
    TOKEN = Str()
    description = Str()


class GetTokenResp(Schema):
    MESSAGE_NAME = Str()
    STATUS = Bool()
    PAYLOAD = Nested(
        GetTokenPayload
    )


class UploadFilePayload(Schema):
    UID_MODEL = Str()
    description = Str()


class UploadFileResp(Schema):
    MESSAGE_NAME = Str()
    STATUS = Bool()
    PAYLOAD = Nested(
        UploadFilePayload
    )


class PredictImagePayload(Schema):
    result = Str()
    description = Str()


class PredictImageResp(Schema):
    MESSAGE_NAME = Str()
    STATUS = Bool()
    PAYLOAD = Nested(
        PredictImagePayload
    )
