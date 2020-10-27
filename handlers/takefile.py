import io
import uuid
import os
from aiohttp.web_response import Response
from aiohttp_apispec import docs, request_schema
from datetime import datetime

from db.schema import all_tokens
from message_schema import CheckTokenReq

from .base import BaseView
from .query import CHECK_TOKEN


class UploadFile(BaseView):
    URL_PATH = r'/{token}/upload_file'

    @property
    def token(self):
        return str(self.request.match_info.get('token'))

    @docs(summary="Загрузка файла")
    async def get(self):
        # TODO 1) добавить запись уникального идентификатора и присвоение уникально идентификатора будущей модели
        # записать все в базу + проверка на токена на валидность

        model_uid = uuid.uuid4().hex

        try:

            reader = await self.request.multipart()
            # /!\ Don't forget to validate your inputs /!\

            archive = await reader.next()

            filename = archive.filename

            # You cannot rely on Content-Length if transfer is chunked.
            size = 0
            with open(os.path.join('test/', filename), 'wb') as f:
                while True:
                    chunk = await archive.read_chunk()  # 8192 bytes by default.
                    if not chunk:
                        break
                    size += len(chunk)
                    f.write(chunk)
        except Exception as e:
            print(e)
            return Response(body={"MESSAGE_NAME": "FILE_UPLOAD_STATUS",
                                  "Status": "UPLOAD_FAIL",
                                  "Payload": {
                                      "description": str(e)
                                  }})

        try:

            query = all_tokens.insert().values((self.token, datetime.now(), model_uid))
            await self.pg.fetch(query)
        except Exception as e:
            print(e)
            return Response(body={"MESSAGE_NAME": "FILE_UPLOAD_STATUS",
                                  "Status": "DB_FAIL",
                                  "Payload": {
                                      "description": str(e)
                                  }})

        return Response(body={"MESSAGE_NAME": "FILE_UPLOAD_STATUS",
                              "Status": "OK",
                              "Payload": {
                                  "UID_MODEL": model_uid,
                                  "description": filename
                              }})
