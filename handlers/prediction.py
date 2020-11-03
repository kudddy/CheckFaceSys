import logging
import face_recognition
import numpy as np
import numpy
import os

from aiohttp.web_response import Response
from aiohttp_apispec import docs, response_schema

from PIL import Image
from io import BytesIO

from .base import BaseView
from message_schema import PredictImageResp

ENCODER_PATH = "facedecoder/temp/encoders"

logging.basicConfig(level=logging.DEBUG)
log = logging.getLogger(__name__)

log.setLevel(logging.DEBUG)


class PredictionHandler(BaseView):
    URL_PATH = r'/{token}/check_similarity/{encoder_uid}/'

    @property
    def encoder_uid(self):
        return str(self.request.match_info.get('encoder_uid'))

    @docs(summary="Предикт по фото", tags=["Basic methods"],
          description="Классификация входящего изображения. "
                      "Присутствует ли оно в датасете, который предоставил клиент.",
          parameters=[
              {
                  'in': 'path',
                  'name': 'token',
                  'schema': {'type': 'string', 'format': 'uuid'},
                  'required': 'true',
                  'description': 'Значение для проверки валидности токена.'
              },
              {
                  'in': 'path',
                  'name': 'encoder_uid',
                  'schema': {'type': 'string', 'format': 'uuid'},
                  'required': 'true',
                  'description': 'Уникальный идентификатор модели, которая обучена на датасете от клиента.'
              }
          ]
          )
    @response_schema(PredictImageResp(), description="В случае успешного валидации токена клиента и наличия валидного "
                                                     "идентификатора модели возвращает имя файка наиболее похоже "
                                                     "персонажа")
    async def get(self):
        try:
            check_update = await self.request.app['cache'].get(b'check_flag')

            if check_update.decode() == self.encoder_uid:
                new_encoder = await self.request.app['encoders'].pickler.async_unpickler(
                    os.path.join(ENCODER_PATH, self.encoder_uid)
                )
                self.request.app['encoders'].update_encoder_by_uid(
                    self.encoder_uid, new_encoder
                )

                await self.request.app['cache'].set(b'check_flag', b'false')

            if self.request.app['encoders'].check_key(self.encoder_uid):

                reader = await self.request.multipart()
                # /!\ Don't forget to validate your inputs /!\

                archive = await reader.next()
                # TODO отвалидировать ответ
                if not archive.filename.endswith("jpg"):
                    return Response(body={"MESSAGE_NAME": "PREDICT_PHOTO",
                                          "STATUS": "PREDICT_FAIL",
                                          "PAYLOAD": {
                                              "result": None,
                                              "description": "wrong file format, try loading a different format"
                                          }})

                arr = []
                while True:
                    chunk = await archive.read_chunk()  # 8192 bytes by default.
                    if not chunk:
                        break
                    arr.append(chunk)

                img_arr = np.array(Image.open(BytesIO(b"".join(arr))))

                input_face_encode = face_recognition.face_encodings(img_arr)
                encoder = self.request.app['encoders'].get_encoder_by_uid(self.encoder_uid)
                # TODO выбарть между базой данных и face_distance
                face_distances = face_recognition.face_distance(encoder['faces_encoders'], input_face_encode[0])
                min_arg = numpy.argmin(face_distances)

                result = encoder['faces_mapping'][min_arg + 1]

                return Response(body={
                    "MESSAGE_NAME": "PREDICT_PHOTO",
                    "STATUS": "OK",
                    "PAYLOAD": {
                        "result": result,
                        "description": "OK"
                    }})
            else:
                return Response(body={
                    "MESSAGE_NAME": "PREDICT_PHOTO",
                    "STATUS": "FAIL",
                    "PAYLOAD": {
                        "result": None,
                        "description": "there is no such model or the model is still being trained, try again later"
                    }
                })
        except Exception as e:
            logging.debug("handler name - %r, message_name - %r, error decoding - %r",
                          "PredictionHandler", "PREDICT_PHOTO", e)
            return Response(body={
                "MESSAGE_NAME": "PREDICT_PHOTO",
                "STATUS": "FAIL",
                "PAYLOAD": {
                    "result": None,
                    "description": "unexpected runtime error"
                }
            })
