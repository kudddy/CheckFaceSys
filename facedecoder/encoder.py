import os
import face_recognition


def get_encoder(image_path: str) -> dict:
    face_encoding = {}
    for image_name in os.listdir(image_path):
        image = face_recognition.load_image_file(os.path.join(image_path, image_name))
        encoding = face_recognition.face_encodings(image)[0]
        face_encoding.update({image_name: encoding})
    return face_encoding
