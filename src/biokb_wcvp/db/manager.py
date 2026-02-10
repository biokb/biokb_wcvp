import io
import logging
import os
import shutil
import sqlite3
import zipfile
from io import BytesIO
from typing import Optional, Type, Union

import pandas as pd
import requests
from sqlalchemy import Engine, create_engine, event, insert, select, text, update
from sqlalchemy.orm import aliased, sessionmaker
from sqlalchemy.orm.session import Session

# Import your models and Base from models.py
from biokb_wcvp.constants import (
    DB_DEFAULT_CONNECTION_STR,
    DEFAULT_PATH_UNZIPPED_DATA_FOLDER,
    DISTRIBUTION_FILE,
    NAMES_FILE,
    PATH_TO_ZIP_FILE,
    TAXONOMY_DATA_FOLDER,
    TAXONOMY_URL,
)
from biokb_wcvp.db import models
from biokb_wcvp.db.tree import Tree
from biokb_wcvp.tools import download_and_unzip

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


@event.listens_for(Engine, "connect")
def set_sqlite_pragma(
    dbapi_connection: sqlite3.Connection, _connection_record: object
) -> None:
    """Enable foreign key constraint for SQLite."""
    if isinstance(dbapi_connection, sqlite3.Connection):
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()


class DbManager:
    """
    Manages database operations, including creating, dropping, and importing data from TSV files.
    """

    def __init__(
        self,
        engine: Optional[Engine] = None,
    ):
        """
        Initialize the DbManager with a database engine and path to the data files.

        Args:
            engine: SQLAlchemy database engine instance.
        """
        connection_str: str = os.getenv("CONNECTION_STR", DB_DEFAULT_CONNECTION_STR)

        self.__engine = engine if engine else create_engine(connection_str)
        if self.__engine.dialect.name == "sqlite":
            with self.__engine.connect() as connection:
                connection.execute(text("pragma foreign_keys=ON"))

        self.Session = sessionmaker(bind=self.__engine)
        self.path_data_folder = DEFAULT_PATH_UNZIPPED_DATA_FOLDER
        logger.info("Engine: %s", self.__engine)

    @property
    def session(self) -> Session:
        """Get a new SQLAlchemy session.

        Returns:
            Session: SQLAlchemy session
        """
        return self.Session()

    def set_import_path(self, path_to_file: Union[str, BytesIO]):
        self.path_to_file = path_to_file

    def recreate_db(self):
        """Drop all tables and recreate them."""
        models.Base.metadata.drop_all(bind=self.__engine)
        models.Base.metadata.create_all(bind=self.__engine)

    def import_data(self, force_download: bool = False, delete_files: bool = False):
        self.recreate_db()
        download_and_unzip(force_download)

        imported: dict[str, int] = {}
        imported.update(self.import_plants())
        logger.info("Plants imported successfully.")
        imported.update(self.import_locations())
        logger.info("Locations imported successfully.")
        self.update_plant_tax_ids()
        logger.info("Tax IDs updated successfully.")
        imported.update(self.import_wgsrpd())
        logger.info("WGS-RPD data imported successfully.")

        if delete_files:
            if os.path.exists(DEFAULT_PATH_UNZIPPED_DATA_FOLDER):
                shutil.rmtree(DEFAULT_PATH_UNZIPPED_DATA_FOLDER)
            if delete_files and os.path.exists(PATH_TO_ZIP_FILE):
                os.remove(PATH_TO_ZIP_FILE)

        return imported

    def extract_and_insert(
        self, df: pd.DataFrame, column_name: str, model: Type[models.Base]
    ):
        """Extract unique values from a DataFrame column and insert them into the database.

            Drops the original column from the DataFrame and replaces it with an ID column.
        Args:
            df (pd.DataFrame): The input DataFrame.
            column_name (str): The name of the column to extract unique values from.
            model (Type[models.Base]): The SQLAlchemy model class corresponding to the table.
        """
        logger.info(f"Importing unique values in table: {model.__tablename__}")
        df_unique = (
            df[[column_name]]
            .dropna()
            .drop_duplicates()
            .reset_index(drop=True)
            .rename_axis("id")
        )
        df_unique.index += 1  # start index from 1
        df = df.merge(
            df_unique.assign(**{f"{column_name}_id": df_unique.index}),
            how="left",
            on=column_name,
        ).drop(columns=[column_name])
        inserted_model = df_unique.rename(columns={column_name: "name"}).to_sql(
            model.__tablename__, con=self.__engine, if_exists="append"
        )
        return df, inserted_model or 0

    def _get_df_names(self) -> pd.DataFrame:
        """Read the names TSV file into a DataFrame."""
        logger.info("Reading names file into DataFrame")
        filepath = os.path.join(self.path_data_folder, NAMES_FILE)
        df = pd.read_csv(filepath, sep="|", low_memory=False)
        df["reviewed"] = df["reviewed"].replace({"N": False, "Y": True})
        df["homotypic_synonym"] = df["homotypic_synonym"].replace({"T": True})
        return df

    def import_plants(self) -> dict[str, int]:
        df = self._get_df_names()
        logger.info("Importing plants")
        # Taxon Rank
        # ============================================================
        df, inserted_taxon_rank = self.extract_and_insert(
            df, "taxon_rank", models.TaxonRank
        )
        # Taxon Status
        # ============================================================
        df, inserted_taxon_status = self.extract_and_insert(
            df, "taxon_status", models.TaxonStatus
        )
        # Family
        # ============================================================
        df, inserted_family = self.extract_and_insert(df, "family", models.Family)

        # Genus
        # ============================================================
        df, inserted_genus = self.extract_and_insert(df, "genus", models.Genus)
        # Infraspecific Rank
        # ============================================================
        df, inserted_infraspecific_rank = self.extract_and_insert(
            df, "infraspecific_rank", models.InfraspecificRank
        )

        # Lifeform Description
        # ============================================================
        df, inserted_lifeform_description = self.extract_and_insert(
            df, "lifeform_description", models.LifeformDescription
        )

        # Climate Description
        # ============================================================
        df, inserted_climate_description = self.extract_and_insert(
            df, "climate_description", models.ClimateDescription
        )

        # Insert Plants
        # ============================================================
        logger.info("Inserting plant names")
        inserted_plants = df.set_index("plant_name_id").to_sql(
            models.Plant.__tablename__,
            con=self.__engine,
            if_exists="append",
            chunksize=10000,
        )

        df_tree, root_id = Tree(
            df=df[["plant_name_id", "parent_plant_name_id"]],
            id_name="plant_name_id",
            parent_id_name="parent_plant_name_id",
        ).get_tree()
        with self.Session.begin() as session:
            root_exists = (
                session.query(models.Plant)
                .filter(models.Plant.plant_name_id == root_id)
                .first()
            )
            if not root_exists:
                root = models.Plant(plant_name_id=root_id, taxon_name="Root")
                session.add(root)

        df_tree = df_tree.where(pd.notnull(df_tree), None)  # type: ignore
        inserted_tree = df_tree.to_sql(
            models.Tree.__tablename__, con=self.__engine, if_exists="append"
        )

        return {
            models.Plant.__tablename__: inserted_plants or 0,
            models.Tree.__tablename__: inserted_tree or 0,
            models.TaxonRank.__tablename__: inserted_taxon_rank or 0,
            models.TaxonStatus.__tablename__: inserted_taxon_status or 0,
            models.Family.__tablename__: inserted_family or 0,
            models.Genus.__tablename__: inserted_genus or 0,
            models.InfraspecificRank.__tablename__: inserted_infraspecific_rank or 0,
            models.LifeformDescription.__tablename__: inserted_lifeform_description
            or 0,
            models.ClimateDescription.__tablename__: inserted_climate_description or 0,
        }

    def import_locations(self) -> dict[str, int]:
        logger.info("Importing locations")

        filepath = os.path.join(
            self.path_data_folder,
            DISTRIBUTION_FILE,
        )
        df = pd.read_csv(filepath, sep="|", low_memory=False)
        df.rename(
            columns={
                "plant_locality_id": "id",
                "plant_name_id": "wcvp_plant_id",
                "region_code_l2": "code_l2",
                "continent_code_l1": "code_l1",
                "area_code_l3": "code_l3",
            },
            inplace=True,
        )
        # ----------------
        # Continents
        # ----------------
        logger.info("Inserting continents")
        df_continent = (
            df[["code_l1", "continent"]]
            .drop_duplicates()
            .rename(columns={"continent": "name"})
            .set_index("code_l1", drop=True)
        ).dropna()
        inserted_continent = df_continent.to_sql(
            models.Continent.__tablename__, con=self.__engine, if_exists="append"
        )
        # ----------------
        # Regions
        # ----------------
        logger.info("Inserting regions")
        df_region = (
            df[["code_l2", "region"]]
            .drop_duplicates()
            .rename(columns={"region": "name"})
            .set_index("code_l2", drop=True)
        ).dropna()
        # ----------------
        # Areas
        # ----------------
        logger.info("Inserting areas")
        inserted_region = df_region.to_sql(
            models.Region.__tablename__, con=self.__engine, if_exists="append"
        )
        df_area = (
            df[["code_l3", "area"]]
            .drop_duplicates()
            .rename(columns={"area": "name"})
            .set_index("code_l3", drop=True)
        ).dropna()
        inserted_area = df_area.to_sql(
            models.Area.__tablename__, con=self.__engine, if_exists="append"
        )
        # ----------------
        # Locations
        # ----------------
        logger.info("Inserting locations")
        df.drop(
            columns=[
                "continent",
                "region",
                "area",
            ],
            inplace=True,
        )
        df.code_l3 = df.code_l3.str.upper()

        inserted_location = df.to_sql(
            models.Location.__tablename__,
            con=self.__engine,
            if_exists="append",
            index=False,
            chunksize=100_000,
        )
        return {
            models.Area.__tablename__: inserted_area or 0,
            models.Location.__tablename__: inserted_location or 0,
            models.Continent.__tablename__: inserted_continent or 0,
            models.Region.__tablename__: inserted_region or 0,
        }

    def __download_taxdmp(self, path_to_file: str):
        """Download the NCBI taxdump file."""
        if not os.path.exists(path_to_file):
            logger.info("Download taxonomy data")
            r = requests.get(
                TAXONOMY_URL,
                allow_redirects=True,
            )
            open(path_to_file, "wb").write(r.content)

    def _import_tax_names(self):
        """Import the taxonomy names.

        Returns:
            Dict[str, int]: table name, number of entries
        """
        logger.info("import taxonomy names (up to 5min)")
        models.TaxonomyName.__table__.drop(self.__engine, checkfirst=True)  # type: ignore
        models.TaxonomyName.__table__.create(self.__engine, checkfirst=True)  # type: ignore
        os.makedirs(TAXONOMY_DATA_FOLDER, exist_ok=True)
        taxtree_path_to_file = os.path.join(TAXONOMY_DATA_FOLDER, "taxdmp.zip")
        self.__download_taxdmp(taxtree_path_to_file)
        archive = zipfile.ZipFile(taxtree_path_to_file, "r")
        names = archive.read("names.dmp")
        df = pd.read_csv(
            io.StringIO(names.decode("utf-8")),
            sep=r"\t\|\t",
            engine="python",
            usecols=[0, 1, 3],
            names=["tax_id", "name", "name_type"],
        )
        df.name_type = df.name_type.str[:-2]
        df.index += 1
        df.index.rename("id", inplace=True)
        df.to_sql(
            models.TaxonomyName.__tablename__,
            self.__engine,
            if_exists="append",
            chunksize=10000,
        )

    def update_plant_tax_ids(self, import_taxonomy_names: bool = True):
        """Update the tax_ids in the plant table.

        Uses NCBI Taxonomy names to find tax_ids for plant names in the plant table.

        First tries to match scientific names, then any name. If still missing, tries to
        inherit tax_id from accepted name.
        """
        logger.info("Update tax_ids in organism table (up to 5min)")
        if import_taxonomy_names:
            self._import_tax_names()

        with self.Session() as session:
            # Scientific name
            logger.info("Update tax_ids by scientific names")
            stmt = (
                update(models.Plant)
                .where(
                    models.Plant.taxon_name == models.TaxonomyName.name,
                    models.TaxonomyName.name_type == "scientific name",
                )
                .values(tax_id=models.TaxonomyName.tax_id)
            )
            session.execute(stmt)
            session.commit()

            # Try any name
            stmt = (
                update(models.Plant)
                .where(
                    models.Plant.taxon_name == models.TaxonomyName.name,
                    models.Plant.tax_id.is_(None),
                )
                .values(tax_id=models.TaxonomyName.tax_id)
            )
            session.execute(stmt)
            session.commit()

            # Inherit tax_id from accepted name
            # Table have to be created fresh each time
            logger.info("Creating temporary table for tax_id inheritance")
            models.TempWcvpPlant.__table__.drop(self.__engine, checkfirst=True)  # type: ignore
            models.TempWcvpPlant.__table__.create(self.__engine, checkfirst=True)  # type: ignore
            stmt = insert(models.TempWcvpPlant).from_select(
                ["plant_name_id", "tax_id"],
                select(models.Plant.plant_name_id, models.Plant.tax_id),
            )
            session.execute(stmt)
            session.commit()

            logger.info("Inherit tax_ids from accepted names")

            p = models.Plant
            tp = models.TempWcvpPlant

            # This version is optimized for MySQL and avoids the "Can't reopen table" error
            stmt = (
                update(p)
                # Referencing tp here tells SQLAlchemy to render a JOIN in MySQL
                .where(p.accepted_plant_name_id == tp.plant_name_id)
                .where(
                    p.plant_name_id != p.accepted_plant_name_id,
                    p.tax_id.is_(None),
                    tp.tax_id.is_not(None),
                )
                .values(tax_id=tp.tax_id)
            )

            session.execute(stmt)
            session.commit()

    def import_wgsrpd(self) -> dict[str, int]:
        """Import World Geographical Scheme for Recording Plant Distributions
        https://www.tdwg.org/standards/wgsrpd/."""
        logger.info("Importing TDWG geoschemes")
        models.GeoLocationLevel3.__table__.drop(self.__engine, checkfirst=True)  # type: ignore
        models.GeoLocationLevel2.__table__.drop(self.__engine, checkfirst=True)  # type: ignore
        models.GeoLocationLevel1.__table__.drop(self.__engine, checkfirst=True)  # type: ignore
        models.GeoLocationLevel1.__table__.create(self.__engine, checkfirst=True)  # type: ignore
        models.GeoLocationLevel2.__table__.create(self.__engine, checkfirst=True)  # type: ignore
        models.GeoLocationLevel3.__table__.create(self.__engine, checkfirst=True)  # type: ignore

        # Implementation goes here
        df_l1 = pd.read_excel(
            "https://github.com/tdwg/geoschemes/raw/refs/heads/main/terrestrial/Level1.xlsx",
            usecols=["L1 code", "L1 continent"],
        )
        df_l1.rename(
            columns={
                "L1 code": "code",
                "L1 continent": "name",
            },
        ).to_sql(
            models.GeoLocationLevel1.__tablename__,
            con=self.__engine,
            if_exists="append",
            index=False,
        )
        df_l2 = pd.read_excel(
            "https://github.com/tdwg/geoschemes/raw/refs/heads/main/terrestrial/Level2.xlsx",
            usecols=["L2 code", "L2 region", "L1 code"],
        )
        df_l2.rename(
            columns={
                "L2 code": "code",
                "L2 region": "name",
                "L1 code": "level_1_code",
            },
        ).to_sql(
            models.GeoLocationLevel2.__tablename__,
            con=self.__engine,
            if_exists="append",
            index=False,
        )
        df_l3 = pd.read_excel(
            "https://github.com/tdwg/geoschemes/raw/refs/heads/main/terrestrial/Level3_27-Jun-25.xlsx",
            usecols=["L3 code", "L3 area", "L2 code"],
        )
        inserted = df_l3.rename(
            columns={
                "L3 code": "code",
                "L3 area": "name",
                "L2 code": "level_2_code",
            },
        ).to_sql(
            models.GeoLocationLevel3.__tablename__,
            con=self.__engine,
            if_exists="append",
            index=False,
        )
        return {models.GeoLocationLevel3.__tablename__: inserted or 0}


def import_data(
    engine: Optional[Engine] = None,
    force_download: bool = False,
    delete_files: bool = True,
) -> dict[str, int]:
    """Import all data in database.

    Args:
        engine (Optional[Engine]): SQLAlchemy engine. Defaults to None.
        force_download (bool, optional): If True, will force download the data, even if
            files already exist. If False, it will skip the downloading part if files
            already exist locally. Defaults to False.
        delete_files (bool, optional): If True, downloaded files are deleted after import.
            Defaults to False.

    Returns:
        dict[str, int]: table=key and number of inserted=value
    """
    db_manager = DbManager(engine)
    return db_manager.import_data(
        force_download=force_download, delete_files=delete_files
    )


def get_session(engine: Optional[Engine] = None) -> Session:
    """Get a new SQLAlchemy session.

    Returns:
        Session: SQLAlchemy session
    """
    db_manager = DbManager(engine)
    return db_manager.session
