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
        user_uid = uuid.uuid4().hex

        query = all_tokens.insert().values((user_uid,))

        await self.pg.fetch(query)

        return Response(body={'token': user_uid})
