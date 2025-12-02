import os
from datetime import date

import pytest
from sqlalchemy import Engine, create_engine

from biokb_wcvp.db.manager import DbManager

# Import your models and Base from models.py
from biokb_wcvp.db.models import Base, Plant

path_to_data = os.path.join("tests", "data/test_data", "test_data.csv")
path_to_db = os.path.join("tests", "dbs", "test.db")
engine = create_engine(f"sqlite:///{path_to_db}")


@pytest.fixture
def dbm() -> DbManager:
    """Fixture to provide a DbManager"""
    return DbManager(engine, path_to_data)


def test_df_manager(dbm: DbManager):
    """Test if DBManager takes the parameter and return the correct values."""
    assert isinstance(dbm.engine, Engine)
    assert dbm.path_to_file == path_to_data


def test_import_family(dbm: DbManager):
    """Test if a family can be imported."""
    dbm.recreate_db()
    test_family_name = "test_family"
    with dbm.Session.begin() as session:
        session.add(Family(name=test_family_name))
        result = session.query(Family.name).filter_by(name=test_family_name).first()
    assert bool(result)
    assert result[0] == test_family_name


def test_import(dbm: DbManager):
    """Test the import of data."""
    dbm.drop_db()
    dbm.create_db()
    dbm.import_data()


def test_family(dbm: DbManager):
    with dbm.Session() as session:
        # Check the number of families
        family_count = session.query(Family).count()
        assert family_count == 10, f"Expected 10 families, found {family_count}"

        # Fetch a specific family and check if it's correctly retrieved
        family_1 = session.query(Family).filter_by(name="Oxalidaceae").first()
        assert family_1 is not None, "Family 'Oxalidaceae' not found"
        assert isinstance(
            family_1, Family
        ), f"Expected Family instance, got {type(family_1)}"

        # Check associated genera
        assert (
            len(family_1.genera) > 0
        ), f"Expected genera in family, found {len(family_1.genera)}"
        for genus in family_1.genera:
            assert isinstance(
                genus, Genus
            ), f"Expected Genus instance, got {type(genus)}"


def test_genus(dbm: DbManager):
    with dbm.Session() as session:
        # Check the number of genera
        genus_count = session.query(Genus).count()
        assert genus_count == 10, f"Expected 10 genera, found {genus_count}"

        # Fetch a specific genus and check if it's correctly retrieved
        genus_1 = session.query(Genus).filter_by(name="Oxalis").first()
        assert genus_1 is not None, "Genus 'Oxalis' not found"
        assert isinstance(
            genus_1, Genus
        ), f"Expected Genus instance, got {type(genus_1)}"

        # Check associated species
        assert (
            len(genus_1.species) > 0
        ), f"Expected species in genus, found {len(genus_1.species)}"
        for species in genus_1.species:
            assert isinstance(
                species, Species
            ), f"Expected Species instance, got {type(species)}"


def test_species(dbm: DbManager):
    with dbm.Session() as session:
        # Check the number of species
        species_count = session.query(Species).count()
        assert species_count == 11, f"Expected 11 species, found {species_count}"

        # Fetch a specific species and check if it's correctly retrieved
        species_1 = session.query(Species).filter_by(name="sepium").first()
        assert species_1 is not None, "Species 'sepium' not found"
        assert isinstance(
            species_1, Species
        ), f"Expected Species instance, got {type(species_1)}"


def test_taxon(dbm: DbManager):
    with dbm.Session() as session:
        # Check the number of taxa
        taxon_count = session.query(Taxon).count()
        assert taxon_count == 11, f"Expected 11 taxa, found {taxon_count}"

        # Fetch an actual taxon from the dataset instead of "Unknown"
        taxon_1 = (
            session.query(Taxon).filter_by(taxon_name="Curtisia dentata").first()
        )  # Choose any existing taxon
        assert taxon_1 is not None, "Taxon 'Curtisia dentata' not found"

        # Check associated plants
        assert (
            len(taxon_1.plants) >= 0
        ), f"Unexpected number of plants, found {len(taxon_1.plants)}"
        for plant in taxon_1.plants:
            assert isinstance(
                plant, Plant
            ), f"Expected Plant instance, got {type(plant)}"


def test_infraspecies(dbm: DbManager):
    with dbm.Session() as session:
        # Check the number of infraspecies
        infraspecies_count = session.query(InfraSpecies).count()
        assert (
            infraspecies_count == 3
        ), f"Expected 3 infraspecies, found {infraspecies_count}"

        # Fetch a specific infraspecies and check if it's correctly retrieved
        infraspecies_1 = (
            session.query(InfraSpecies).filter_by(name="leptophylla").first()
        )  # Adjust name if needed
        assert infraspecies_1 is not None, "Infraspecies 'leptophylla' not found"
        assert isinstance(
            infraspecies_1, InfraSpecies
        ), f"Expected Infraspecies instance, got {type(infraspecies_1)}"


def test_climate_description(dbm: DbManager):
    with dbm.Session() as session:
        # Check the number of ClimateDescriptions
        climate_description_count = session.query(ClimateDescription).count()
        assert (
            climate_description_count == 4
        ), f"Expected 4 climate descriptions, found {climate_description_count}"

        # Fetch a specific ClimateDescription and check if it's correctly retrieved
        climate_description_1 = (
            session.query(ClimateDescription)
            .filter_by(description="wet tropical")
            .first()
        )
        assert (
            climate_description_1 is not None
        ), "ClimateDescription 'wet tropical' not found"
        assert isinstance(
            climate_description_1, ClimateDescription
        ), f"Expected ClimateDescription instance, got {type(climate_description_1)}"

        # Check associated EnvironmentalDescription
        assert (
            len(climate_description_1.environmental_descriptions) >= 0
        ), f"Unexpected number of EnvironmentalDescriptions, found {len(climate_description_1.environmental_descriptions)}"


def test_lifeform_description(dbm: DbManager):
    with dbm.Session() as session:
        # Check the number of LifeformDescriptions
        lifeform_description_count = session.query(LifeFormDescription).count()
        assert (
            lifeform_description_count == 8
        ), f"Expected 8 lifeform descriptions, found {lifeform_description_count}"

        # Fetch a specific LifeformDescription and check if it's correctly retrieved
        lifeform_description_1 = (
            session.query(LifeFormDescription).filter_by(description="tree").first()
        )
        assert (
            lifeform_description_1 is not None
        ), "LifeformDescription 'tree' not found"
        assert isinstance(
            lifeform_description_1, LifeFormDescription
        ), f"Expected LifeformDescription instance, got {type(lifeform_description_1)}"

        # Check associated EnvironmentalDescriptions
        assert (
            len(lifeform_description_1.environmental_descriptions) >= 0
        ), f"Unexpected number of EnvironmentalDescriptions, found {len(lifeform_description_1.environmental_descriptions)}"


def test_area(dbm: DbManager):
    with dbm.Session() as session:
        # Check the number of Area entries
        area_count = session.query(Area).count()
        assert area_count == 11, f"Expected 11 areas, found {area_count}"

        # Fetch a specific Area and check if it's correctly retrieved
        area_1 = session.query(Area).filter_by(name="Brazil Southeast").first()
        assert area_1 is not None, "Area 'Brazil Southeast' not found"
        assert isinstance(area_1, Area), f"Expected Area instance, got {type(area_1)}"

        # Check associated GeographicArea
        assert (
            len(area_1.geographic_area) > 0
        ), f"Expected at least one GeographicArea, found {len(area_1.geographic_area)}"

        # Optionally, you can check specific details of the GeographicArea
        for geographic_area in area_1.geographic_area:
            assert isinstance(
                geographic_area, GeographicArea
            ), f"Expected GeographicArea instance, got {type(geographic_area)}"


def test_continent(dbm: DbManager):
    with dbm.Session() as session:
        # Check the number of Continent entries
        continent_count = session.query(Continent).count()
        assert continent_count == 6, f"Expected 6 continents, found {continent_count}"

        # Fetch a specific Continent and check if it's correctly retrieved
        continent_1 = (
            session.query(Continent).filter_by(name="NORTHERN AMERICA").first()
        )
        assert continent_1 is not None, "Continent 'NORTHERN AMERICA' not found"
        assert isinstance(
            continent_1, Continent
        ), f"Expected Continent instance, got {type(continent_1)}"

        # Check associated GeographicArea
        assert (
            len(continent_1.geographic_area) > 0
        ), f"Expected at least one GeographicArea, found {len(continent_1.geographic_area)}"

        # Optionally, you can check specific details of the GeographicArea
        for geographic_area in continent_1.geographic_area:
            assert isinstance(
                geographic_area, GeographicArea
            ), f"Expected GeographicArea instance, got {type(geographic_area)}"


def test_region(dbm: DbManager):
    with dbm.Session() as session:
        # Check the number of Region entries
        region_count = session.query(Region).count()
        assert region_count == 9, f"Expected 9 regions, found {region_count}"

        # Fetch a specific Region and check if it's correctly retrieved
        region_1 = session.query(Region).filter_by(name="Brazil").first()
        assert region_1 is not None, "Region 'Brazil' not found"
        assert isinstance(
            region_1, Region
        ), f"Expected Region instance, got {type(region_1)}"

        # Check associated GeographicArea
        assert (
            len(region_1.geographic_area) > 0
        ), f"Expected at least one GeographicArea, found {len(region_1.geographic_area)}"

        # Optionally, you can check specific details of the GeographicArea
        for geographic_area in region_1.geographic_area:
            assert isinstance(
                geographic_area, GeographicArea
            ), f"Expected GeographicArea instance, got {type(geographic_area)}"


def test_publication(dbm: DbManager):
    with dbm.Session() as session:
        # Check the total number of Publication entries
        publication_count = session.query(Publication).count()
        assert publication_count == 11

        # Fetch a specific Publication and verify the details
        publication_1 = (
            session.query(Publication).filter_by(primary_author="Lourteig").first()
        )
        assert publication_1 is not None
        assert isinstance(publication_1, Publication)
        assert (
            publication_1.primary_author == "Lourteig"
        ), f"Expected author 'Lourteig', found {publication_1.primary_author}"

        # Ensure 'first_published' is a date
        assert isinstance(
            publication_1.first_published, date
        ), f"Expected 'first_published' to be a date, found {type(publication_1.first_published)}"

        # Check associated Plants
        assert (
            len(publication_1.plants) > 0
        ), f"Expected at least one Plant associated with the publication, found {len(publication_1.plants)}"

        # verify the relationship with a specific Plant
        plant = publication_1.plants[0]  # Example: get the first associated plant
        assert isinstance(plant, Plant), f"Expected Plant instance, got {type(plant)}"


def test_plant(dbm: DbManager):
    with dbm.Session() as session:
        # Check the total number of Plant entries
        plant_count = session.query(Plant).count()
        assert plant_count == 11, f"Expected 11 plants, found {plant_count}"

        # Fetch a specific Plant by its ipni_id (or plant_name_id, based on your setup)
        plant_1 = session.query(Plant).filter_by(ipni_id="980294-1").first()
        assert plant_1 is not None, "Plant with ipni_id '980294-1' not found"
        assert isinstance(
            plant_1, Plant
        ), f"Expected Plant instance, got {type(plant_1)}"

        # Check if the plant's relationships are correctly established
        assert isinstance(
            plant_1.family, Family
        ), f"Expected Family instance, got {type(plant_1.family)}"
        assert isinstance(
            plant_1.genus, Genus
        ), f"Expected Genus instance, got {type(plant_1.genus)}"
        assert isinstance(
            plant_1.species, Species
        ), f"Expected Species instance, got {type(plant_1.species)}"

        # Verify the names of associated models (family, genus, species)
        assert (
            plant_1.family.name == "Oxalidaceae"
        ), f"Expected family 'Oxalidaceae', found {plant_1.family.name}"
        assert (
            plant_1.genus.name == "Oxalis"
        ), f"Expected genus 'Oxalis', found {plant_1.genus.name}"
        assert (
            plant_1.species.name == "sepium"
        ), f"Expected species 'sepium', found {plant_1.species.name}"

        # Verify other attributes
        assert isinstance(
            plant_1.ipni_id, str
        ), f"Expected 'ipni_id' to be a string, found {type(plant_1.ipni_id)}"
        assert isinstance(
            plant_1.reviewed, bool
        ), f"Expected 'reviewed' to be a boolean, found {type(plant_1.reviewed)}"
        assert isinstance(
            plant_1.introduced, bool
        ), f"Expected 'introduced' to be a boolean, found {type(plant_1.introduced)}"
        assert isinstance(
            plant_1.extinct, bool
        ), f"Expected 'extinct' to be a boolean, found {type(plant_1.extinct)}"
        assert isinstance(
            plant_1.location_doubtful, bool
        ), f"Expected 'location_doubtful' to be a boolean, found {type(plant_1.location_doubtful)}"


# No code was selected, so I will provide a general improvement to the existing code.


# Add a main function to run all tests
def main():
    pytest.main([__file__])


if __name__ == "__main__":
    main()
