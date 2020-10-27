from aiohttp.web_response import Response
from aiohttp_apispec import docs, request_schema


from .base import BaseView
from message_schema import CheckTokenReq


class CheckToken(BaseView):
    URL_PATH = r'/{token}/token_status'

    @property
    def token(self):
        return str(self.request.match_info.get('token'))

    @docs(summary="Проверка на наличие токена")
    @request_schema(CheckTokenReq())
    async def get(self):
        # TODO по токену нужна дополнительная информация сколько и какие идентификаторы моделей присутствуют в системе
        # Валиден не валиден
        # # TODO валидация ответа

        return Response(body={'token_status': True})
