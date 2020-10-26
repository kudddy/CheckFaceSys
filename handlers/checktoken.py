from aiohttp.web_response import Response
from aiohttp.web_urldispatcher import View
from aiohttp_apispec import docs, request_schema, response_schema
from message_schema import CheckTokenReq

# TODO должны получать из базы данных
VALID_TOKEN = ['123', '2222']


class CheckToken(View):
    URL_PATH = r'/token_status/{token}'

    @property
    def token(self):
        return str(self.request.match_info.get('token'))

    @docs(summary="Проверка на наличие токена")
    @request_schema(CheckTokenReq())
    async def get(self):
        if self.token in VALID_TOKEN:
            token_status = True
        else:
            token_status = False
        # TODO валидация ответа
        return Response(body={'token_status': token_status})

