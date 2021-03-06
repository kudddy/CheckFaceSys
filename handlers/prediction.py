import logging
import face_recognition
import numpy as np
import numpy

from aiohttp.web_response import Response
from aiohttp_apispec import docs, response_schema

from PIL import Image
from io import BytesIO

from .base import BaseView
from .query import GET_ENCODER_UID
from db.schema import done_encoders
from message_schema import PredictImageResp

ENCODER_PATH = "facedecoder/temp/encoders"

logging.basicConfig(level=logging.DEBUG)
log = logging.getLogger(__name__)

log.setLevel(logging.DEBUG)


class PredictionHandler(BaseView):
    URL_PATH = r'/{token}/check_similarity/{encoder_uid}/{n}/'

    @property
    def encoder_uid(self):
        return str(self.request.match_info.get('encoder_uid'))

    @property
    def n(self):
        return int(self.request.match_info.get('n'))

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
              },
              {
                  'in': 'path',
                  'name': 'n',
                  'schema': {'type': 'string', 'format': 'uuid'},
                  'required': 'true',
                  'description': 'Кол-во наиболее близких соседей'
              }
          ]
          )
    @response_schema(PredictImageResp(), description="В случае успешного валидации токена клиента и наличия валидного "
                                                     "идентификатора модели возвращает имя файка наиболее похоже "
                                                     "персонажа")
    async def get(self):
        try:
            # обновляем кэш всех копий приложений если контент обновлен
            can_predict: bool = False
            # проверяем есть ли в приложении
            if self.encoders.check_key(self.encoder_uid):
                can_predict = True
            else:
                # проверяем если энкодеры в базе
                # сделано для синхронизации в случае если запускается несколько копий приложений
                query = GET_ENCODER_UID.where(done_encoders.c.encoders_uid == self.encoder_uid)

                result = await self.pg.fetch(query)

                if len(result) > 0:
                    self.encoder.get_all_encoder_by_hdd_async()
                    can_predict = True

            if can_predict:
                reader = await self.request.multipart()
                # /!\ Don't forget to validate your inputs /!\

                image = await reader.next()
                # TODO отвалидировать ответ
                if not image.filename.endswith("jpg"):
                    return Response(body={"MESSAGE_NAME": "PREDICT_PHOTO",
                                          "STATUS": False,
                                          "PAYLOAD": {
                                              "result": None,
                                              "description": "wrong file format, try loading a different format"
                                          }})

                arr = []
                while True:
                    chunk = await image.read_chunk()  # 8192 bytes by default.
                    if not chunk:
                        break
                    arr.append(chunk)

                img_arr = np.array(Image.open(BytesIO(b"".join(arr))))

                input_face_encode = face_recognition.face_encodings(img_arr)
                encoder = self.request.app['encoders'].get_encoder_by_uid(self.encoder_uid)
                # TODO выбарть между базой данных и face_distance
                face_distances = face_recognition.face_distance(encoder['faces_encoders'], input_face_encode[0])

                min_args = numpy.argsort(face_distances)[:self.n]

                result = [encoder['faces_mapping'][x + 1] for x in min_args]

                return Response(body={
                    "MESSAGE_NAME": "PREDICT_PHOTO",
                    "STATUS": True,
                    "PAYLOAD": {
                        "result": result,
                        "description": "OK"
                    }})
            else:
                return Response(body={
                    "MESSAGE_NAME": "PREDICT_PHOTO",
                    "STATUS": False,
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
                "STATUS": False,
                "PAYLOAD": {
                    "result": None,
                    "description": "unexpected runtime error"
                }
            })
