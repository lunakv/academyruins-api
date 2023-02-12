import os
from pathlib import Path

from app.utils.logger import logger

from . import static_paths as paths


def seed_dir(path):
    if not Path(path).is_dir():
        logger.warning(f"Creating directory {path}...")
        os.makedirs(path)


async def seed():
    logger.info("Making sure necessary directories exist...")
    seed_dir(paths.__dir)
    seed_dir(paths.cr_dir)


if __name__ == "__main__":
    seed()
