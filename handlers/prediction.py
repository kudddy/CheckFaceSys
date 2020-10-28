from aiohttp.web_response import Response
from aiohttp_apispec import docs, request_schema


from .base import BaseView
from message_schema import CheckTokenReq


class PredictionHandler(BaseView):
    URL_PATH = r'/{token}/check_similarity'

    @property
    def token(self):
        return str(self.request.match_info.get('token'))

    @docs(summary="Предикт по фото")
    async def get(self):

        # проверяем в кэше есть ли в memcached (на предмет обновления для внутренненого словаря с энкодерами)
        await self.request.app['cache'].set(b'testkey', b'test')

        data = await self.request.app['cache'].get(b'testkey')

        print(data)
        if data:
            # TODO тут мы обновляем словарь нашего энкодера
            # словарь нужно добавить в requests
            pass
        # если нет то проверям на на наличие в локальном словаре

        # если нет в локально словаре то шлем сообщение о том что модель еще не готова

        # если да то отправляем ответ

        return Response(body={'token_status': data.decode()})