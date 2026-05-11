import os
from pathlib import Path

# standard for all biokb projects, but individual set
PROJECT_NAME = "wcvp"
BASIC_NODE_LABEL = "DbWCVP"
# standard for all biokb projects
ORGANIZATION = "biokb"
LIBRARY_NAME = f"{ORGANIZATION}_{PROJECT_NAME}"
HOME = str(Path.home())
BIOKB_FOLDER = os.getenv("BIOKB_FOLDER", os.path.join(HOME, f".{ORGANIZATION}"))
PROJECT_FOLDER = os.path.join(BIOKB_FOLDER, PROJECT_NAME)
DATA_FOLDER = os.path.join(PROJECT_FOLDER, "data")
EXPORT_FOLDER = os.path.join(DATA_FOLDER, "ttls")
ZIPPED_TTLS_PATH = os.path.join(DATA_FOLDER, "ttls.zip")
SQLITE_PATH = os.path.join(BIOKB_FOLDER, f"{ORGANIZATION}.db")
DB_DEFAULT_CONNECTION_STR = "sqlite:///" + SQLITE_PATH
NEO4J_PASSWORD = "neo4j_password"
NEO4J_URI = "bolt://localhost:7687"
NEO4J_USER = "neo4j"
LOGS_FOLDER = os.path.join(DATA_FOLDER, "logs")  # where to store log files
TABLE_PREFIX = PROJECT_NAME + "_"
os.makedirs(DATA_FOLDER, exist_ok=True)


# not standard for all biokb projects
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

BALKAN_AREA_CODES = [
    "ALB",  # Albania
    "BUL",  # Bulgaria
    "GRC",  # Greece (Mainland and most islands)
    "KRI",  # Kriti (Crete)
    "ROM",  # Romania
    "TUE",  # Turkey-in-Europe (East Thrace)
    "YUG",  # Former Yugoslavia (Includes: BSN, CRO, KOS, MKD, MNE, SRB, SLO)
    "EAI",  # East Aegean Islands (Floristically distinct part of Greece)
]

MEDITERANIAN_AREA_CODES = [
    # Southern Europe / Balkans
    "ALB",
    "BUL",
    "GRC",
    "ITA",
    "ROM",
    "TUE",
    "YUG",  # Includes: BSN, CRO, KOS, MKD, MNE, SRB, SLO
    "SPA",  # Includes: GIB (Gibraltar)
    "POR",  # Portugal
    # Mediterranean Islands (Level 3)
    "BAL",  # Baleares
    "COR",  # Corse (Corsica)
    "KRI",  # Kriti (Crete)
    "SAR",  # Sardegna (Sardinia)
    "SIC",  # Sicilia (Includes Malta)
    "CYP",  # Cyprus
    "EAI",  # East Aegean Islands
    # North Africa
    "ALG",
    "EGY",
    "LBY",
    "MOR",
    "TUN",
    # Western Asia / Levant
    "LBS",  # Lebanon-Syria (Includes LBN, SYR)
    "PAL",  # Palestine (Includes ISR, JOR, PAL)
    "TUR",  # Turkey (Anatolia)
    # Microstates
    "MON",  # Monaco
]

TDWG_BASE_URL = "https://github.com/tdwg/geoschemes/raw/refs/heads/main/terrestrial/"
TDWG_L1_URL = TDWG_BASE_URL + "Level1.xlsx"
TDWG_L2_URL = TDWG_BASE_URL + "Level2.xlsx"
TDWG_L3_URL = TDWG_BASE_URL + "Level3_27-Jun-25.xlsx"
