from pathlib import Path
from uuid import uuid4

from concurrent.futures import ThreadPoolExecutor
import asyncio

from misc.config import Paths


pool = ThreadPoolExecutor()


def get_temp_file_path(extension: str = None) -> Path:
    return Path(
        Paths.temp_dir,
        str(uuid4()) + ("" if extension.startswith(".") else ".") + (extension if extension else "")
    )


def threadpool(func):
    def wrapper(*args, **kwargs):
        return asyncio.wrap_future(pool.submit(func, *args, **kwargs))

    return wrapper
