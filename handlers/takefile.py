import logging
import uuid
import os
from aiohttp.web_response import Response
from aiohttp_apispec import docs, response_schema
from datetime import datetime

from db.schema import all_tokens
from message_schema import UploadFileResp

from .base import BaseView


ZIP_PATH = "facedecoder/temp/zip"

logging.basicConfig(level=logging.DEBUG)
log = logging.getLogger(__name__)

log.setLevel(logging.DEBUG)


class UploadFile(BaseView):
    URL_PATH = r'/{token}/upload_file'

    @property
    def token(self):
        return str(self.request.match_info.get('token'))

    @docs(summary="Загрузка файла",
          tags=["Basic methods"],
          description="Загрузка zip архива с фотографиями. На данный момент возможна загрузка только zip файла, "
                      "где внутри лежит папка с именем Image в которой есть фотографии для обучения в формате jpg. "
                      "Каждая фотография в названии должна иметь уникальный идентификатор который будет возвращать "
                      "сервис в случай успешного обнаружения лица. Формат form-data.",
          parameters=[{
              'in': 'path',
              'name': 'token',
              'schema': {'type': 'string', 'format': 'uuid'},
              'required': 'true',
              'description': 'Значение для проверки валидности токена.'
          }]
          )
    @response_schema(UploadFileResp,
                     description="Возвращает статус обратки и уникальный идентификатор модели по которой в "
                                 "дальнейшем будет производиться классификация.")
    async def get(self):

        model_uid = uuid.uuid4().hex

        try:
            # TODO привести в порядок
            reader = await self.request.multipart()
            # /!\ Don't forget to validate your inputs /!\

            archive = await reader.next()

            if not archive.filename.endswith("zip"):
                return Response(body={"MESSAGE_NAME": "FILE_UPLOAD_STATUS",
                                      "STATUS": False,
                                      "PAYLOAD": {
                                          "UID_MODEL": None,
                                          "description": "wrong file format, try loading a different format"
                                      }})

            # You cannot rely on Content-Length if transfer is chunked.
            size = 0
            with open(os.path.join(ZIP_PATH, model_uid), 'wb') as f:
                while True:
                    chunk = await archive.read_chunk()  # 8192 bytes by default.
                    if not chunk:
                        break
                    size += len(chunk)
                    f.write(chunk)

            # await self.request.app['cache'].set(b'update', model_uid.encode())
            await self.request.app.input_queue.put(model_uid)
        except Exception as e:
            logging.debug("handler name - %r, message_name - %r, error decoding - %r",
                          "UploadFile", "FILE_UPLOAD_STATUS", e)
            return Response(body={"MESSAGE_NAME": "FILE_UPLOAD_STATUS",
                                  "STATUS": False,
                                  "PAYLOAD": {
                                      "UID_MODEL": None,
                                      "description": str(e)
                                  }})

        try:
            query = all_tokens.insert().values((self.token, datetime.now(), model_uid))
            await self.pg.fetch(query)
        except Exception as e:
            logging.debug("handler name - %r, message_name - %r, error decoding - %r",
                          "UploadFile", "FILE_UPLOAD_STATUS", e)
            return Response(body={"MESSAGE_NAME": "FILE_UPLOAD_STATUS",
                                  "STATUS": False,
                                  "PAYLOAD": {
                                      "UID_MODEL": None,
                                      "description": str(e)
                                  }})

        return Response(body={"MESSAGE_NAME": "FILE_UPLOAD_STATUS",
                              "STATUS": True,
                              "PAYLOAD": {
                                  "UID_MODEL": model_uid,
                                  "description": archive.filename
                              }})
