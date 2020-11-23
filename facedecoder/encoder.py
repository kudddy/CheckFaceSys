import os
import pickle
import zipfile
import face_recognition
from os import rename, path


def get_encoder(image_path: str, encoder_path: str, use_filesystem=True) -> dict:
    """
    Преобразования фото в вектор
    :param image_path: Путь к папке с фотографиями
    :param encoder_path: Путь в который нужно сохранить кодер
    :param use_filesystem:
    :return:
    """
    faces_encoders: list = []
    faces_mapping: dict = {}
    status: bool = True

    counter = 0
    for face_count, image_name in enumerate(os.listdir(image_path)):
        try:
            image = face_recognition.load_image_file(os.path.join(image_path, image_name))
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

    # если словарь пустой, то отправляем отрицательный статус
    if counter == 0:
        status = False

    res = {"faces_encoders": faces_encoders, "faces_mapping": faces_mapping, "status": status}
    if use_filesystem:
        with open(encoder_path, 'wb') as f:
            pickle.dump(res, f)
    return res


def extract_zip(zip_path: str, image_path: str) -> bool:
    try:
        status = zipfile.is_zipfile(zip_path)
        if status:
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:

                zip_ref.extractall(image_path)
                members = zip_ref.filename

                temp = members.split("/")[-1]

                rename(path.join(image_path, "image"), path.join(image_path, temp))
            return True
        else:
            return False
    except Exception as e:
        print(e)
        return False
