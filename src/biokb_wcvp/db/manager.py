import logging
import os
import re
from datetime import datetime
from io import BytesIO
from typing import Optional, Union

import pandas as pd
from sqlalchemy import Engine, create_engine
from sqlalchemy.orm import sessionmaker

# Import your models and Base from models.py
from biokb_wcvp.constants import (
    DB_DEFAULT_CONNECTION_STR,
    DEFAULT_PATH_UNZIPPED_DATA_FOLDER,
)
from biokb_wcvp.db import models
from biokb_wcvp.tools import download_and_unzip

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class DbManager:
    """
    Manages database operations, including creating, dropping, and importing data from TSV files.
    """

    def __init__(
        self,
        engine: Optional[Engine] = None,
        force_download: bool = False,
    ):
        """
        Initialize the DbManager with a database engine and path to the data files.

        Args:
            engine: SQLAlchemy database engine instance.
            path_to_file (str): Path to the directory containing TSV files.
        """
        connection_str = os.getenv("CONNECTION_STR", DB_DEFAULT_CONNECTION_STR)
        self.engine = engine if engine else create_engine(connection_str)
        self.Session = sessionmaker(bind=self.engine)
        self.path_data_folder = DEFAULT_PATH_UNZIPPED_DATA_FOLDER
        self.force_download = force_download

    def set_import_path(self, path_to_file: Union[str, BytesIO]):
        self.path_to_file = path_to_file

    def recreate_db(self):
        """Drop all tables and recreate them."""
        models.Base.metadata.drop_all(bind=self.engine)
        models.Base.metadata.create_all(bind=self.engine)

    def import_data(self, force_download=False):
        self.recreate_db()
        download_and_unzip(force_download)

        imported = {}
        imported["plants"] = self.import_plants()
        logger.info("Plants imported successfully.")
        imported["locations"] = self.import_locations()
        logger.info("Locations imported successfully.")
        return imported

    def import_plants(self):
        filepath = os.path.join(self.path_data_folder, "wcvp_names.csv")
        df = pd.read_csv(filepath, sep="|", low_memory=False)
        df.rename(
            columns={
                "plant_name_id": "id",
            },
            inplace=True,
        )
        df["genus_hybrid"] = df["genus_hybrid"].replace(
            {"+": "graft-chimaera", "×": "hybrid"}
        )
        df["species_hybrid"] = df["species_hybrid"].replace(
            {"+": "graft-chimaera", "×": "hybrid"}
        )
        df["reviewed"] = df["reviewed"].replace({"N": False, "Y": True})
        df["homotypic_synonym"] = df["homotypic_synonym"].replace({"T": True})
        return df.to_sql(
            models.Plant.__tablename__,
            con=self.engine,
            if_exists="append",
            index=False,
            chunksize=10000,
        )

    def import_locations(self):
        filepath = os.path.join(self.path_data_folder, "wcvp_distribution.csv")
        df = pd.read_csv(filepath, sep="|", low_memory=False)
        df.rename(
            columns={
                "plant_locality_id": "id",
                "plant_name_id": "wcvp_plant_id",
            },
            inplace=True,
        )
        return df.to_sql(
            models.Location.__tablename__,
            con=self.engine,
            if_exists="append",
            index=False,
            chunksize=10000,
        )
