import uuid
from aiohttp.web_response import Response
from aiohttp_apispec import docs

from db.schema import all_tokens

from .base import BaseView


class CreateToken(BaseView):
    URL_PATH = r'/create_token'

    @docs(summary="Создание токена для пользователя")
    async def get(self):
        # TODO должна быть какая нибудь аутентификация (причем быстрая)
        try:
            user_uid = uuid.uuid4().hex

            query = all_tokens.insert().values((user_uid,))

            await self.pg.fetch(query)

            return Response(body={
                "MESSAGE_NAME": "GET_TOKEN",
                "STATUS": "OK",
                "payload": {
                    "TOKEN": user_uid
                }
            })
        except Exception as e:
            # TODO добавить логирование ошибок везде
            print(e)
            return Response(body={
                "MESSAGE_NAME": "GET_TOKEN_FAIL",
                "STATUS": "FAIL",
                "payload": {
                    "description": "unknown runtime error"
                }
            })
