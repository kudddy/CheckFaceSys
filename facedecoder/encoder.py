import os
import pickle

import face_recognition


def get_encoder(image_path: str, encoder_path: str, use_filesystem=True) -> None:
    faces_encoders = []
    faces_mapping = {}
    counter = 0
    for face_count, image_name in enumerate(os.listdir(image_path)):
        print(image_name)
        try:
            image = face_recognition.load_image_file(os.path.join(image_path, image_name))
            # TODO проблема с поворотом(если лицо чуть повернуто, то ничего не видно)
            # в апи нужно давать возможность выбирать (быстрый способ или медленный)
            encoding = face_recognition.face_encodings(image)
            if len(encoding) > 0:
                for number_face, face_encoder in enumerate(encoding):
                    faces_encoders.append(face_encoder)
                    counter += 1
                    faces_mapping.update({counter: image_name})
            else:
                print("ignoring file")
        except Exception as e:
            print(e)
    if use_filesystem:
        with open(encoder_path, 'wb') as f:
            pickle.dump({
                "faces_encoders": faces_encoders,
                "faces_mapping": faces_mapping
            }, f)
