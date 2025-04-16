import os
import re
from datetime import datetime
from io import BytesIO
from typing import Optional, Union

import pandas as pd
from sqlalchemy import Engine, create_engine
from sqlalchemy.orm import sessionmaker

# Import your models and Base from models.py
from wcvp.constants import DB_DEFAULT_CONNECTION_STR
from wcvp.db.models import (
    Area,
    Base,
    ClimateDescription,
    Continent,
    EnvironmentalDescription,
    Family,
    Genus,
    GeographicArea,
    InfraSpecies,
    LifeFormDescription,
    Plant,
    Publication,
    Region,
    Species,
    Taxon,
    TaxonRank,
    TaxonStatus,
)

# Path to the CSV file and SQLite database file
path_to_file = r"tests/data/test_data/test_data.csv"
sqlite_file_path = "sqlite:///tests/data/dbs/test_data.db"
# MYSQL_DB_URL = "mysql+pymysql://root:PASSWORD@localhost/db_name"


def clean_date(date_str: str):
    if isinstance(date_str, str):
        # Remove parentheses and extract the year
        date_str = re.sub(r"[^\d]", "", date_str)  # Removes non-digit characters
        try:
            return datetime.strptime(date_str, "%Y").date()  # Converts to a date object
        except ValueError:
            return None  # In case the date format is incorrect or empty
    return None


class DbManager:
    """
    Manages database operations, including creating, dropping, and importing data from TSV files.
    """

    def __init__(
        self,
        engine: Optional[Engine] = None,
        path_data_folder: Optional[str] = None,
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
        self.path_data_folder = path_data_folder
        self.force_download = force_download

    @property
    def all_tables_have_data(self):
        self.create_db()  # create tables if not exists
        with self.Session() as session:
            exists = []
            for model in (
                Area,
                ClimateDescription,
                Continent,
                EnvironmentalDescription,
                Family,
                Genus,
                GeographicArea,
                InfraSpecies,
                LifeFormDescription,
                Plant,
                Publication,
                Region,
                Species,
                Taxon,
                TaxonRank,
                TaxonStatus,
            ):
                exists.append(session.query(model).count())
        return all(exists)

    def set_import_path(self, path_to_file: Union[str, BytesIO]):
        self.path_to_file = path_to_file

    def create_db(self):
        """Create all tables defined in the Base class."""
        Base.metadata.create_all(bind=self.engine)

    def drop_db(self):
        """Drop all tables defined in the Base class."""
        Base.metadata.drop_all(bind=self.engine)

    def recreate_db(self):
        """Drop all tables and recreate them."""
        self.drop_db()
        self.create_db()

    def get_or_create(self, session, model, **kwargs):
        """new_method
        Fetch an instance of the model based on the given criteria, or create it if it doesn't exist.

        Args:
            session: SQLAlchemy session object.
            model: SQLAlchemy model class (e.g., Family, Genus, Author).
            **kwargs: Criteria to filter the model (e.g., name="Acanthaceae").

        Returns:
            Instance of the model.
        """
        try:
            # Ensure the session is still active
            instance = session.query(model).filter_by(**kwargs).first()
            if not instance:
                instance = model(**kwargs)
                session.add(instance)
            session.flush()
            return instance
        except Exception as e:
            session.rollback()
            raise e

    def import_data(self, only_if_db_empty=False):
        if only_if_db_empty and self.all_tables_have_data:
            return
        self.recreate_db()
        self.import_names()

    def import_names(self):
        pass
