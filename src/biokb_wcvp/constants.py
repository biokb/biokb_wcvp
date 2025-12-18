"""Basic constants."""

import os
from enum import StrEnum
from pathlib import Path

HOME = str(Path.home())
BIOKB_FOLDER = os.path.join(HOME, ".biokb")
PROJECT_NAME = "wcvp"
PROJECT_FOLDER = os.path.join(BIOKB_FOLDER, PROJECT_NAME)
DATA_FOLDER = os.path.join(PROJECT_FOLDER, "data")
LOGS_FOLDER = os.path.join(DATA_FOLDER, "logs")  # where to store log files
ZIPPED_TTLS_PATH = os.path.join(DATA_FOLDER, "ttls.zip")

DOWNLOAD_URL = "https://sftp.kew.org/pub/data-repositories/WCVP/wcvp.zip"
PATH_TO_ZIP_FILE = os.path.join(DATA_FOLDER, "wcvp.zip")
DEFAULT_PATH_UNZIPPED_DATA_FOLDER = os.path.join(DATA_FOLDER, "unzipped")
SQLITE_PATH = os.path.join(BIOKB_FOLDER, "biokb.db")
DB_DEFAULT_CONNECTION_STR = "sqlite:///" + SQLITE_PATH


DISTRIBUTION_FILE = "wcvp_distribution.csv"
NAMES_FILE = "wcvp_names.csv"


TAXONOMY_URL = "https://ftp.ncbi.nlm.nih.gov/pub/taxonomy/taxdmp.zip"
# TODO: check other libs if they also load data to this folder
TAXONOMY_DATA_FOLDER = os.path.join(BIOKB_FOLDER, "taxtree", "data")

BASIC_NODE_LABEL = "DbWCVP"
EXPORT_FOLDER = os.path.join(DATA_FOLDER, "ttls")

NEO4J_USER = "neo4j"
NEO4J_PASSWORD = "neo4j_password"
NEO4J_URI = "bolt://localhost:7687"
