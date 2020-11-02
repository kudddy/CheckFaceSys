from aiohttp.web_response import Response
from aiohttp_apispec import docs, request_schema, response_schema

from .base import BaseView
from message_schema import CheckTokenReq


class CheckToken(BaseView):
    URL_PATH = r'/{token}/token_status'

    @property
    def token(self):
        return str(self.request.match_info.get('token'))

    @docs(tags=["Basic methods"],
          summary="Валидация токена",
          description='Проверка токена на валидность',
          parameters=[{
              'in': 'path',
              'name': 'token',
              'schema': {'type': 'string', 'format': 'uuid'},
              'required': 'true',
              'description': 'Значение для проверки валидности токена.'
          }]
          )
    # @request_schema(CheckTokenReq())
    @response_schema(CheckTokenReq(),
                     description="Возвращает json с именем сообщения "
                                 "и статусом валидности токена")
    async def get(self):
        # TODO по токену нужна дополнительная информация сколько и какие идентификаторы моделей присутствуют в системе
        # Валиден не валиден
        # # TODO валидация ответа

        return Response(body={"MESSAGE_NAME": "CHECK_TOKEN",
                              "TOKEN_STATUS": True})
