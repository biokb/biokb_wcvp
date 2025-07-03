import logging
import os
import urllib.request
import zipfile

from biokb_wcvp.constants import (
    DATA_FOLDER,
    DEFAULT_PATH_UNZIPPED_DATA_FOLDER,
    DOWNLOAD_URL,
    PATH_TO_ZIP_FILE,
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def download_and_unzip(force_download: bool = False) -> str:
    """Download WCVP data in local download folder, unzipped and return path.

    Args:
        force (bool, optional): Force to download the file. Defaults to False.

    Returns:
        str: path to the unzipped data folder.
    """
    os.makedirs(DATA_FOLDER, exist_ok=True)
    if force_download or not os.path.exists(PATH_TO_ZIP_FILE):
        urllib.request.urlretrieve(DOWNLOAD_URL, PATH_TO_ZIP_FILE)
        logger.info(f"{DOWNLOAD_URL} downloaded to {PATH_TO_ZIP_FILE}")
    else:
        logger.info(f"{PATH_TO_ZIP_FILE} already exists. Skipping download.")

    with zipfile.ZipFile(PATH_TO_ZIP_FILE, "r") as zip_ref:
        os.makedirs(DEFAULT_PATH_UNZIPPED_DATA_FOLDER, exist_ok=True)
        zip_ref.extractall(DEFAULT_PATH_UNZIPPED_DATA_FOLDER)

    return DEFAULT_PATH_UNZIPPED_DATA_FOLDER
