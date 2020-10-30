import pickle
import aiofiles


class Pickler:
    def __init__(self):
        self.open = aiofiles.open

    async def async_pickler(self, obj):
        async with self.open('foo.pickle', 'wb') as f:
            pickled_foo = pickle.dumps(obj)
            await f.write(pickled_foo)

    async def async_unpickler(self, path: str):
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
