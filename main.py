import uvicorn
from backend.config import DB_SETTINGS
from backend.api import *


if __name__ == "__main__":
    uvicorn.run(app, host=DB_SETTINGS['DOMAIN'], port=DB_SETTINGS['PORT'])
