import re
from datetime import datetime
from io import BytesIO
from typing import Union

import pandas as pd
from sqlalchemy import Engine, create_engine, exc
from sqlalchemy.orm import sessionmaker

# Import your models and Base from models.py
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


class DbManager:
    def __init__(self, engine, filepath: str = None):
        """
        Initialize DbManager class.

        Args:
            engine: SQLAlchemy engine object.
            filepath: Path to the CSV file containing data.
        """
        self.engine: Engine = engine
        self.path_to_file = filepath
        self.Session = sessionmaker(bind=engine)

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
        """
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

    def get_df(self):
        """
        Read the CSV file and return a pandas DataFrame.

        Returns:
            Pandas DataFrame.
        """
        return pd.read_csv(self.path_to_file, sep=",")

    def import_data(self):
        self.recreate_db()
        df = self.get_df()

        with self.Session.begin() as session:
            for index, r in df.iterrows():

                # Replace NaN values with appropriate defaults
                row = r.fillna(
                    {
                        "family": "Unknown",
                        "genus": "Unknown",
                        "primary_author": "Unknown",
                        "parenthetical_author": "Unknown",
                        "place_of_publication": "Unknown",
                        "volume_and_page": "Unknown",
                        "first_published": "Unknown",
                        "area_code_l3": "Unknown",
                        "area": "Unknown",
                        "region_code_l2": 0,
                        "region": "Unknown",
                        "continent_code_l1": 0,
                        "continent": "Unknown",
                        "geographic_area": "Unknown",
                        "species": "Unknown",
                        "infraspecific_rank": "Unknown",
                        "infraspecies": "Unknown",
                        "taxon_status": "Unknown",
                        "taxon_name": "Unknown",
                        "hybrid_formula": "Unknown",
                        "replaced_synonym_author": "Unknown",
                        "homotypic_synonym": False,
                        "introduced": False,
                        "extinct": False,
                        "location_doubtful": False,
                        "lifeform_description": "Unknown",
                        "climate_description": "Unknown",
                    }
                )

                # Fetch or create family and genus
                family = self.get_or_create(
                    session,
                    Family,
                    name=row["family"] if not pd.isna(row["family"]) else "Unknown",
                )
                genus = self.get_or_create(
                    session,
                    Genus,
                    name=row["genus"] if not pd.isna(row["genus"]) else "Unknown",
                    family_id=family.id,
                )

                # Fetch or create species and taxon
                species = self.get_or_create(
                    session,
                    Species,
                    name=row["species"] if not pd.isna(row["species"]) else "Unknown",
                    genus_id=genus.id,
                )
                taxon_name = (
                    row["taxon_name"] if row["taxon_name"] != "Unknown" else "Unknown"
                )
                # Get or create taxon status and taxon rank
                taxon_rank = self.get_or_create(
                    session,
                    TaxonRank,
                    rank=(
                        row["taxon_rank"]
                        if not pd.isna(row["taxon_rank"])
                        else "Unknown"
                    ),
                )
                taxon_status = self.get_or_create(
                    session,
                    TaxonStatus,
                    status=(
                        row["taxon_status"]
                        if not pd.isna(row["taxon_status"])
                        else "Unknown"
                    ),
                )

                # Get or create taxon with references to rank and status
                existing_taxon = (
                    session.query(Taxon).filter_by(taxon_name=taxon_name).first()
                )
                if not existing_taxon:
                    taxon = Taxon(
                        taxon_name=taxon_name,
                        rank_id=taxon_rank.id,
                        status_id=taxon_status.id,
                    )
                    session.add(taxon)
                    session.flush()

                # Fetch or create infraspecies
                infraspecies = self.get_or_create(
                    session,
                    InfraSpecies,
                    name=(
                        row["infraspecies"]
                        if not pd.isna(row["infraspecies"])
                        else "Unknown"
                    ),
                )

                def clean_date(date_str):
                    if isinstance(date_str, str):
                        # Remove parentheses and extract the year
                        date_str = re.sub(
                            r"[^\d]", "", date_str
                        )  # Removes non-digit characters
                        try:
                            return datetime.strptime(
                                date_str, "%Y"
                            ).date()  # Converts to a date object
                        except ValueError:
                            return None  # In case the date format is incorrect or empty
                    return None

                # Fetch or create publication instance
                publication = self.get_or_create(
                    session,
                    Publication,
                    primary_author=(
                        row["primary_author"]
                        if not pd.isna(row["primary_author"])
                        else "Unknown"
                    ),
                    first_published=(
                        clean_date(row["first_published"])
                        if not pd.isna(row["first_published"])
                        else None
                    ),
                )

                # Fetch or create climate description
                climate_description = self.get_or_create(
                    session,
                    ClimateDescription,
                    description=(
                        row["climate_description"]
                        if not pd.isna(row["climate_description"])
                        else "Unknown"
                    ),
                )

                # Fetch or create lifeform description
                lifeform_description = self.get_or_create(
                    session,
                    LifeFormDescription,
                    description=(
                        row["lifeform_description"]
                        if not pd.isna(row["lifeform_description"])
                        else "Unknown"
                    ),
                )

                # Fetch EnvironmentalDescription instance
                existing_environmental_description = (
                    session.query(EnvironmentalDescription)
                    .filter_by(
                        lifeform_id=lifeform_description.id,
                        climate_id=climate_description.id,
                    )
                    .first()
                )
                if not existing_environmental_description:
                    # Create the EnvironmentalDescription instance
                    environmental_description = EnvironmentalDescription(
                        lifeform_id=lifeform_description.id,
                        climate_id=climate_description.id,
                    )

                    session.add(environmental_description)
                    session.flush()
                else:
                    environmental_description = existing_environmental_description

                # Fetch or create the Area, Region, and Continent instances
                area = self.get_or_create(
                    session,
                    Area,
                    code=(
                        row["area_code_l3"]
                        if not pd.isna(row["area_code_l3"])
                        else None
                    ),
                    name=row["area"] if not pd.isna(row["area"]) else "Unknown",
                )

                region = self.get_or_create(
                    session,
                    Region,
                    code=(
                        row["region_code_l2"]
                        if not pd.isna(row["region_code_l2"])
                        else None
                    ),
                    name=row["region"] if not pd.isna(row["region"]) else "Unknown",
                )

                continent = self.get_or_create(
                    session,
                    Continent,
                    code=(
                        row["continent_code_l1"]
                        if not pd.isna(row["continent_code_l1"])
                        else None
                    ),
                    name=(
                        row["continent"] if not pd.isna(row["continent"]) else "Unknown"
                    ),
                )

                # Fetch or create the GeographicArea instance
                geo_name = (
                    row["geographic_area"]
                    if not pd.isna(row["geographic_area"])
                    else "Unknown"
                )
                existing_area = (
                    session.query(GeographicArea).filter_by(name=geo_name).first()
                )
                if not existing_area:
                    # Create the GeographicArea instance
                    geographic_area = GeographicArea(
                        name=geo_name,
                        area_id=area.id,
                        region_id=region.id,
                        continent_id=continent.id,
                    )
                    session.add(geographic_area)
                    session.flush()
                else:
                    geographic_area = existing_area

                # Fetch or create the Plant instance based on plant_name_id
                existing_plant = (
                    session.query(Plant)
                    .filter_by(plant_name_id=row["plant_name_id"])
                    .first()
                )

                if not existing_plant:
                    # Create the Plant instance
                    plant = Plant(
                        plant_name_id=row["plant_name_id"],
                        reviewed=bool(row["reviewed"]),
                        ipni_id=row["ipni_id"],
                        introduced=bool(row["introduced"]),
                        extinct=bool(row["extinct"]),
                        location_doubtful=bool(row["location_doubtful"]),
                        family_id=family.id,
                        genus_id=genus.id,
                        publication_id=publication.id,
                        taxon_id=taxon.id,
                        geographic_area_id=geographic_area.id,
                        environmental_description_id=environmental_description.id,
                        species_id=species.id,
                        infraspecies_id=infraspecies.id,
                    )
                    # Add the Plant instance to the session
                    session.add(plant)
                    session.flush()
                else:
                    plant = existing_plant
