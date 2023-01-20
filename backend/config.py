import yaml
from os.path import abspath, join, exists
from os import makedirs, getenv

from backend.library.func import str_to_bool


DEFAULT_WORK_DIR = abspath(join(abspath(__file__), '../..'))
DATA_DIR = join(DEFAULT_WORK_DIR, 'data')

conf_filename = 'conf.yaml'

try:
    settings = yaml.safe_load(open(join(DEFAULT_WORK_DIR, conf_filename)))
except FileNotFoundError:
    settings = {}

PYTEST_RUN_CONFIG = getenv('PYTEST_RUN_CONFIG')
IS_TEST = str_to_bool(PYTEST_RUN_CONFIG) if PYTEST_RUN_CONFIG else False
SECRET_KEY = settings.get('SECRET_KEY', 'secret')
ALGORITHM = settings.get('ALGORITHM', 'HS256')
ACCESS_TOKEN_EXPIRE_MINUTES = settings.get('ACCESS_TOKEN_EXPIRE_MINUTES', 1440)

DB_SETTINGS = settings.get('DB', {})
DB_SETTINGS['DOMAIN'] = DB_SETTINGS.get('DOMAIN', '127.0.0.1')
DB_SETTINGS['PORT'] = DB_SETTINGS.get('PORT', 8000)
DB_NAME = DB_SETTINGS.get('NAME', None)
DB_USER = DB_SETTINGS.get('USER', 'postgres')
DB_ASYNC = False if IS_TEST else DB_SETTINGS.get('ASYNC', False)

for f in [DATA_DIR]:
    if not exists(f):
        makedirs(f, exist_ok=True)
