import logging

from aiohttp.web_response import Response
from aiohttp_apispec import docs, response_schema

from db.schema import all_tokens
from .base import BaseView
from .query import GET_MODEL
from message_schema import CheckTokenResp

logging.basicConfig(level=logging.DEBUG)
log = logging.getLogger(__name__)

log.setLevel(logging.DEBUG)


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
    @response_schema(CheckTokenResp(),
                     description="Возвращает json с именем сообщения"
                                 ", статусом валидности токена и списком моделей.")
    async def get(self):
        try:

            query = GET_MODEL.where(all_tokens.c.token == self.token)

            result = await self.pg.fetch(query)

            return Response(body={"MESSAGE_NAME": "CHECK_TOKEN",
                                  "STATUS": True,
                                  "PAYLOAD": {
                                      "TOKEN_STATUS": True,
                                      "NAME_MODELS": result,
                                      "description": None}
                                  })

        except Exception as e:
            logging.debug("handler name - %r, message_name - %r, error decoding - %r",
                          "CheckToken", "CHECK_TOKEN", e)
            return Response(body={"MESSAGE_NAME": "CHECK_TOKEN",
                                  "STATUS": False,
                                  "PAYLOAD": {
                                      "TOKEN_STATUS": None,
                                      "NAME_MODELS": [],
                                      "description": "Неизвестная runtime ошибка"}
                                  })
