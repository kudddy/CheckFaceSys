from aiohttp.web_response import Response
from aiohttp_apispec import docs
import uuid

from db.schema import all_tokens

from .base import BaseView

# TODO должны получать из базы данных
VALID_TOKEN = ['123', '2222']


class CreateToken(BaseView):
    URL_PATH = r'/create_token'

    @docs(summary="Создание токена для пользователя")
    async def get(self):
        user_uid = uuid.uuid4().hex

        query = all_tokens.insert().values((user_uid,))

        await self.pg.fetch(query)

        return Response(body={'token': user_uid})
