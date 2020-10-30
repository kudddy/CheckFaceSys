from aiohttp.web_response import Response
from aiohttp_apispec import docs, request_schema

import face_recognition
from io import BytesIO
import numpy as np
from PIL import Image
import numpy
import os

from .base import BaseView
from message_schema import CheckTokenReq

ENCODER_PATH = "facedecoder/temp/encoders"


class PredictionHandler(BaseView):
    URL_PATH = r'/{token}/check_similarity/{encoder_uid}/'

    @property
    def encoder_uid(self):
        return str(self.request.match_info.get('encoder_uid'))

    @docs(summary="Предикт по фото")
    async def get(self):
        # проверяем в кэше есть ли в memcached (на предмет обновления для внутренненого словаря с энкодерами)
        # await self.request.app['cache'].set(b'check_flag', b'test')

        # check_update = await self.request.app['cache'].get(b'testkey')
        #
        # if check_update:
        #     # TODO тут мы обновляем словарь нашего энкодера
        #     # словарь нужно добавить в requests
        #     pass

        # запрос с payload

        # проверяем есть ли у очереди сообщение для encoder_uid

        check_update = await self.request.app['cache'].get(b'check_flag')

        if check_update.decode() == self.encoder_uid:
            print("обновились")
            new_encoder = await self.request.app['encoders'].pickler.async_unpickler(
                os.path.join(ENCODER_PATH, self.encoder_uid)
            )
            self.request.app['encoders'].update_encoder_by_uid(
                self.encoder_uid, new_encoder
            )

            # после обновления присваеваем значение  false флагу

            await self.request.app['cache'].set(b'check_flag', b'false')

        if self.request.app['encoders'].check_key(self.encoder_uid):

            # TODO проверка есть в кэше нужный

            reader = await self.request.multipart()
            # /!\ Don't forget to validate your inputs /!\

            archive = await reader.next()
            # TODO отвалидировать ответ

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
                    "recognition_name": result
                }})
        else:
            return Response(body={
                "MESSAGE_NAME": "PREDICT_PHOTO",
                "STATUS": "FAIL",
                "payload": {
                    "description": "there is no such model or the model is still being trained, try again later"
                }
            })
