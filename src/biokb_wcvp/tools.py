import os
import urllib.request
import zipfile
from logging import getLogger
from typing import Optional

from dotenv import load_dotenv
from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine
from sqlalchemy.exc import OperationalError

from biokb_wcvp.constants import (
    DATA_FOLDER,
    DB_DEFAULT_CONNECTION_STR,
    DEFAULT_PATH_UNZIPPED_DATA_FOLDER,
    DOWNLOAD_URL,
    PATH_TO_ZIP_FILE,
)

logger = getLogger(__name__)


def get_engine(
    connection_string: Optional[str] = None, env: Optional[str] = None
) -> Optional[Engine]:
    """Get a SQLAlchemy engine based on the provided connection string or environment file.
    The function prioritizes environment variables in the following order:
        1. .env file with CONNECTION_STR variable (if exists)
        2. -e/--env option specifying the environment file
        3. -c/--connection-string option specifying the connection string directly
        4. Default connection string (sqlite:///~/.biokb/biokb.db)
    Args:
        connection_string (Optional[str]): SQLAlchemy engine URL (default: None)
        env (Optional[str]): Environment file to load for configuration (default: None)
    Returns:
        Optional[Engine]: SQLAlchemy engine if connection string is valid, otherwise None
    """
    engine: Engine | None = None
    if connection_string:
        try:
            engine = create_engine(connection_string)
            # check if the engine can connect to the database
            with engine.connect() as con:
                con.execute(text("SELECT 1"))
        except OperationalError as e:
            raise ValueError(
                "Failed to create engine with provided connection string. Please check the connection string and try again. "
                f"Original error: {e}"
            )
    elif env:
        # check if the provided env file exists
        if not os.path.exists(env):
            raise ValueError(
                f"Provided environment file {env} does not exist. Please provide a valid environment "
                "file or specify the connection string directly with the -c argument."
            )
        logger.info(f"Loading CONNECTION_STR variables from {env} file.")
        load_dotenv(env, override=True)
        connection_string = os.getenv("CONNECTION_STR")
        if connection_string is None:
            raise ValueError(
                f"CONNECTION_STR environment variable not found in {env} file. Please provide a valid environment "
                "file with CONNECTION_STR or specify the connection string directly with the -c argument."
            )
        engine = create_engine(connection_string)
        try:
            with engine.connect() as con:
                con.execute(text("SELECT 1"))
        except OperationalError as e:
            raise ValueError(
                f"Failed to create engine with connection string \n'{connection_string}'\n from environment file {env}. Please check the connection string in the environment file and try again."
                f"Original error: {e}"
            )
    elif os.path.exists(".env"):
        logger.info("Loading CONNECTION_STR variables from .env file.")
        load_dotenv(".env", override=True)
        connection_string = os.getenv("CONNECTION_STR")
        if connection_string is None:
            raise ValueError(
                "CONNECTION_STR environment variable not found in .env file. "
                "Please provide a valid .env file or specify the connection string directly with the -c argument."
            )
        engine = create_engine(connection_string)
        try:
            with engine.connect() as con:
                con.execute(text("SELECT 1"))
        except OperationalError as e:
            raise ValueError(
                f"Failed to create engine with connection string \n'{connection_string}'\n from .env file. Please check the connection string in the .env file and try again."
                f"Original error: {e}"
            )
    if connection_string is None:
        logger.info(
            f"No environment file provided or CONNECTION_STR not found. Using default connection string {DB_DEFAULT_CONNECTION_STR}."
        )

    return engine


def download_and_unzip(force_download: bool = False) -> str:
    """Download WCVP data in local download folder, unzipped and return path.

    Args:
        force (bool, optional): Force to download the file. Defaults to False.

    Returns:
        str: path to the unzipped data folder.
    """
    os.makedirs(DATA_FOLDER, exist_ok=True)
    if force_download or not os.path.exists(PATH_TO_ZIP_FILE):
        logger.info("Downloading data")
        urllib.request.urlretrieve(DOWNLOAD_URL, PATH_TO_ZIP_FILE)
    else:
        logger.info(f"{PATH_TO_ZIP_FILE} already exists. Skipping download.")

    with zipfile.ZipFile(PATH_TO_ZIP_FILE, "r") as zip_ref:
        os.makedirs(DEFAULT_PATH_UNZIPPED_DATA_FOLDER, exist_ok=True)
        zip_ref.extractall(DEFAULT_PATH_UNZIPPED_DATA_FOLDER)

    return DEFAULT_PATH_UNZIPPED_DATA_FOLDER
