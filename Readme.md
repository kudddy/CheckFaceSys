##  GROUPBY Face
Сервис агрегирования и преобразования данных для поиска по лицах на входе
## Запуск приложения
#### Вариант 1

Локальный запуск приложения без обязки supervisor и nginx.
TODO:
написать про конфиги + добавить в репозиторий config_sample
###### Шаг 1
Установка зависимостей:
```
source venv/bin/activate
pip install -r requirements.txt
```
###### Шаг 2
Для запуска в папке utils создать конфиг secret.json и настроить его(пример есть в файле secret_sample.json), 
установить параметр debug - false и выполнить следующую команду:
```
python main.py
```
#### Вариант 2

Запуск приложения с supervisor и nginx, но для этого требуется установить supervisor и nginx, либо просто воспользоваться
вариантом 3, где приложение упаковано в Docker.
###### Шаг 1
Повторить шаг 1 из Варианта 1
###### Шаг 2
Выполнить следующую команду:
```
start.sh
```
#### Вариант 3
Запуск полностью готового к деплою приложения с nginx, supervisor внутри контейнера
###### Шаг 1
Собираем образ
```
docker build -t GroupByFace .
```
###### Шаг 2
Запускаем образ
```
docker run  -p 8080:8080 GroupByFace
```
#### Вариант 4
Запуск группы приложений через docker-compose:
```
docker-compose up -d
```

Приложение доступно по адесу: http://127.0.0.1:8080, который выдаст swagger иструкцию и описание основных методов

## Использование Alembic
Установка alembic
```
pip install alembic
```
Инициализация alembic
```
alembic init alembic
```
Изменение в init настройки аутентификации для бд
```
sqlalchemy.url = driver://user:pass@localhost/dbname
```
Начало сессии обновления базы. Название процедуры
```
alembic revision -m "create account table"
```
Описанием того что хотим сделать
```
def upgrade():
    op.create_table(
        'account',
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('name', sa.String(50), nullable=False),
        sa.Column('description', sa.Unicode(200)),
    )

def downgrade():
    op.drop_table('account')
```

Запуск процедуры
```
alembic upgrade head
```

## Проблемы
Нет общей памяти для нескольких процессов(требуется внести механизм обновленрия кэша для все fork процесов)
Добавить защиту от спама
При установке face recognition требуется дополнительно установить пакет cmake, который
почему то не входит в список зависимостей фреймворка
