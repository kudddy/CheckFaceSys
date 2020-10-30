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

        model_uid = uuid.uuid4().hex

        try:
            # TODO привести в порядок
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
                                  "STATUS": "UPLOAD_FAIL",
                                  "payload": {
                                      "description": str(e)
                                  }})

        try:
            query = all_tokens.insert().values((self.token, datetime.now(), model_uid))
            await self.pg.fetch(query)
        except Exception as e:
            print(e)
            return Response(body={"MESSAGE_NAME": "FILE_UPLOAD_STATUS",
                                  "STATUS": "DB_FAIL",
                                  "payload": {
                                      "description": str(e)
                                  }})

        return Response(body={"MESSAGE_NAME": "FILE_UPLOAD_STATUS",
                              "STATUS": "OK",
                              "payload": {
                                  "UID_MODEL": model_uid,
                                  "description": filename
                              }})
