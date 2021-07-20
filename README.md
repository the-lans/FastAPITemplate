# FastAPITemplate
Шаблон для построения API с помощью фреймворка FastAPI и ORM Peewee. Для аутентификации используется JWT.



## Установка

Последовательность действий для установки:

- Для создания виртуальной среды могут использоваться *conda* или *virtualenv*.

- Создайте виртуальное окружение `conda create -n venv`

- Активируйте виртуальное окружение `conda activate venv`

- Установите пакеты `pip install -r requirements.txt`

- Перейдите в папку с проектом 

- Создайте базу данных \<database\>

- Выполните миграцию `python pw_migrate.py migrate --database=postgresql://postgres@<host_postgres>:5432/<database>`

  \<host_postgres\> - рабочий хост базы данных

  \<database\> - имя базы данных

- Настройте конфигурационный файл *conf.yaml*

- Запустите API `uvicorn main:app --reload`

  

## Отладка

Запустите на отладку файл `main.py`

Проверьте API на локальной машине: http://127.0.0.1:8000/

Доступ к REST API Swagger: http://127.0.0.1:8000/docs#/

Доступ к REST API Redoc: http://127.0.0.1:8000/redoc



## Разработка

Для форматирования кода используйте утилиту *black*

`black --config ./pyproject.toml -v -S ./`

