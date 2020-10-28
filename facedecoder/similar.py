import face_recognition
import numpy


def get_similar_photo(input_image: list):
    # input_image = face_recognition.load_image_file(name_input_file)
    encoding_input_img = face_recognition.face_encodings(input_image)
    if len(encoding_input_img) == 0:
        return -1
    else:
        encoding_input_img = encoding_input_img[0]
    # face_distances = face_recognition.face_distance(dict_usage_encodings[variations]['know_encoding'],
    #                                                 encoding_input_img)
    min_arg = numpy.argmin(face_distances)
    # name = dict_usage_encodings[variations]['dict_mapping'][min_arg]
    return name
