from aiohttp.web_response import Response
from aiohttp_apispec import docs, request_schema

from db.schema import all_tokens
from message_schema import CheckTokenReq

from .base import BaseView
from .query import CHECK_TOKEN


class CheckToken(BaseView):
    URL_PATH = r'/token_status/{token}'

    @property
    def token(self):
        return str(self.request.match_info.get('token'))

    @docs(summary="Проверка на наличие токена")
    @request_schema(CheckTokenReq())
    async def get(self):
        # TODO по токену нужна дополнительная информация сколько и какие идентификаторы моделей присутствуют в системе
        # Валиден не валиден

        query = CHECK_TOKEN.where(all_tokens.c.token == self.token)

        result = await self.pg.fetch(query)

        if len(result) > 0:
            token_status = True
        else:
            token_status = False

        # TODO валидация ответа
        return Response(body={'token_status': token_status})
