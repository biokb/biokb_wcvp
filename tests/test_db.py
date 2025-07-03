import pandas as pd
import pytest
from sqlalchemy import create_engine

from biokb_wcvp.db import models
from biokb_wcvp.db.manager import DbManager


@pytest.fixture
def db_manager() -> DbManager:
    """
    Creates a temporary SQLite database for test
    """
    engine = create_engine(f"sqlite://")  # in memory
    db_manager = DbManager(engine=engine, path_data_folder="tests/data")
    return db_manager


class TestDbManager:
    def test_create_db(self, db_manager: DbManager):
        db_manager.recreate_db()
        tables = models.Base.metadata.tables.keys()
        tables_expected: list[str] = [
            "family",
            "taxon_rank",
            "taxon_status",
            "infraspecies",
            "lifeform_description",
            "climate_description",
            "continent",
            "region",
            "area",
            "publication",
            "genus",
            "taxon",
            "environmental_description",
            "geographic_area",
            "species",
            "plant",
        ]
        tables_expected_with_prefix = {models.Base._prefix + x for x in tables_expected}
        assert set(tables) == tables_expected_with_prefix
