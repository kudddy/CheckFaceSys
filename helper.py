import pickle
import aiofiles
import os


class Pickler:
    def __init__(self):
        self.open = aiofiles.open

    async def async_unpickler(self, obj):
        async with self.open('foo.pickle', 'wb') as f:
            pickled_foo = pickle.dumps(obj)
            await f.write(pickled_foo)

    async def async_pickler(self, path: str):
        async with self.open(path, 'rb') as f:
            pickled_foo = await f.read()

        return pickle.loads(pickled_foo)

    @staticmethod
    def sync_pickler(filename: str):
        """
        Получение пикл файла
        """
        with open(filename, 'rb') as f:
            d_ = pickle.load(f)
        return d_

    @staticmethod
    def sync_unpickler(obj, filename: str):
        """
        Дамп объекта
        Вход: объект, имя файла
        """
        with open(filename, 'wb') as f:
            pickle.dump(obj, f)


def check_folder_in_path():
    path = 'facedecoder/temp'
    i = 0
    for temp in os.listdir(path):
        if temp in ('encoders', 'image', 'zip'):
            i += 1
    if i != 3:
        [os.makedirs(os.path.join(path, x)) for x in ('encoders', 'image', 'zip')]
