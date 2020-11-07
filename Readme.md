##  GROUPBY Face
Сервис агрегирования и преобразования данных для поиска по лицах на входе
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

## Запуск rabbit для Dramatiq
```
docker run -p 15672:15672 -p 5672:5672 -d --hostname my-rabbit --name some-rabbit rabbitmq:3-management
```

## Проблемы
Нет общей памяти для нескольких процессов(требуется внести механизм обновленрия кэша для все fork процесов)
При установке face recognition требуется дополнительно установить пакет cmake, который
почему то не входит в список зависимостей фреймворка
