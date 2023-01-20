from typing import Dict, Optional, Any
from os.path import join
import uuid
from fastapi import UploadFile

from backend.config import DATA_DIR


def upload_file(
    file: UploadFile, ret: Optional[Dict[str, Any]] = None, chunk_size: int = 10240
) -> (Dict[str, Any], Optional[str]):
    if ret is None:
        ret = {}
    filename = join(DATA_DIR, str(uuid.uuid4()) + ".csv")
    try:
        with open(filename, 'wb') as f:
            while contents := file.file.read(chunk_size):
                f.write(contents)
    except Exception:
        return {"success": False, "message": "There was an error uploading the file"}, None
    finally:
        file.file.close()
    return ret, filename


def upload_body(body: bytes, ret: Optional[Dict[str, Any]] = None) -> (Dict[str, Any], Optional[str]):
    if ret is None:
        ret = {}
    filename = join(DATA_DIR, str(uuid.uuid4()) + ".csv")
    try:
        with open(filename, 'wb') as f:
            f.write(body)
    except Exception:
        return {"success": False, "message": "There was an error uploading the file"}, None
    return ret, filename
