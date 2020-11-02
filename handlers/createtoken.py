import uuid

from aiohttp.web_response import Response
from aiohttp_apispec import docs, response_schema

from db.schema import all_tokens
from message_schema import GetTokenResp
from .base import BaseView


class CreateToken(BaseView):
    URL_PATH = r'/create_token'

    @docs(summary="Создание токена",
          tags=["Basic methods"],
          description="Создание токена, на выходе уникальный токен пользвателя по которому в дальнейшем будет "
                      "проходить аутентификация.")
    @response_schema(GetTokenResp(),
                     description="Возвращает имя сообщения, статус и payload в котором есть либо описание ошибки либо "
                                 "токен по которому в дальнейшем будет происходить аутентификация. Его нужно "
                                 "обязательно сохранить!")
    async def get(self):
        # TODO должна быть какая нибудь аутентификация (причем быстрая)
        try:
            user_uid = uuid.uuid4().hex

            query = all_tokens.insert().values((user_uid,))

            await self.pg.fetch(query)

            return Response(body={
                "MESSAGE_NAME": "GET_TOKEN",
                "STATUS": "OK",
                "PAYLOAD": {
                    "TOKEN": user_uid,
                    "description": "OK"
                }
            })
        except Exception as e:
            # TODO добавить логирование ошибок везде
            print(e)
            return Response(body={
                "MESSAGE_NAME": "GET_TOKEN",
                "STATUS": "FAIL",
                "PAYLOAD": {
                    "TOKEN": None,
                    "description": "unknown runtime error"
                }
            })
