import logging
import os
from contextlib import asynccontextmanager
from datetime import datetime
from io import BytesIO
from typing import Annotated, List, LiteralString, Optional

from fastapi import Depends, FastAPI, File, HTTPException, Query, status
from fastapi.responses import JSONResponse
from sqlalchemy import create_engine, or_
from sqlalchemy.orm import Session

from wcvp.api import schemas
from wcvp.api.tags import Tag
from wcvp.db import manager, models

"""
# MySQL Database credentials
DB_USER = os.getenv("DB_USER", "wcvp_user")
DB_PASSWORD = os.getenv("DB_PASSWORD", "wcvp_passwd")
DB_HOST = os.getenv("DB_HOST", "0.0.0.0")
DB_NAME = os.getenv("DB_NAME", "wcvp_db")
DB_PORT = os.getenv("DB_PORT", "3307")  # MySQL is running on 3307

# SQLAlchemy connection URL
DATABASE_URL = f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

engine = create_engine(DATABASE_URL)
"""

"""
sqlite_file_name = "fastapi.db"
sqlite_file_path = os.path.join("tests", "dbs", sqlite_file_name)
sqlite_url: LiteralString = f"sqlite:///{sqlite_file_path}"
connect_args = {"check_same_thread": False}
engine = create_engine(sqlite_url, connect_args=connect_args)
"""
sqlite_file_name = "fastapi.db"
sqlite_file_path = os.path.join("tests", "dbs", sqlite_file_name)

conn_url = (
    os.environ["CONNECTION_STR"]
    if "CONNECTION_STR" in os.environ.keys()
    else f"sqlite:///{sqlite_file_path}"
)
engine: manager.Engine = create_engine(conn_url)

dbm = manager.DbManager(engine)

logger = logging.getLogger(__name__)
logging.basicConfig(
    filename="fast_api.log",
    datefmt="%m/%d/%y %H:%M:%S",  # https://docs.python.org/3/library/time.html#time.strftime
    format="%(levelname)s %(name)s %(asctime)s - %(message)s",
    filemode="a",
    level=logging.DEBUG,
)


# dbm = manager.DbManager(engine)


def get_session():
    session: Session = dbm.Session()
    try:
        yield session
    finally:
        session.close()


@asynccontextmanager
async def lifespan(app: FastAPI):
    # dbm.drop_db()
    dbm.create_db()
    yield
    # Clean up
    pass


app = FastAPI(lifespan=lifespan)


@app.get(path="/")
def hello_world() -> dict[str, str]:
    """Say hello."""
    return {"msg": "Hello World"}


# tag: Database Management
# ========================


@app.post(path="/load_db_from_csv/", tags=[Tag.DBMANAGE])
def load_db_from_file(file: Annotated[bytes, File()]):
    """Load a csv file in database."""
    dbm.drop_db()
    dbm.create_db()
    loaded = False
    if file:
        dbm.set_import_path(BytesIO(file))
        dbm.import_data()
        loaded = True
    return {"loaded": loaded}


# tag: Family
# ========================
@app.post(path="/family/create/", response_model=schemas.Family, tags=[Tag.FAMILY])
def create_family(
    family_create: schemas.FamilyCreate, session: Session = Depends(get_session)
) -> models.Family:
    """Creates a new family with the name `name` in the database.

    The id of the family is autoincrement. If a family with the same name
    already exists, the existing family is returned.
    """
    existing_family: models.Family | None = (
        session.query(models.Family).filter_by(name=family_create.name).first()
    )
    if existing_family:
        family: models.Family = existing_family
    else:
        new_family = models.Family(name=family_create.name)
        session.add(new_family)
        session.commit()
        session.refresh(new_family)
        family: models.Family = new_family
    return family


# get one family by id
@app.get("/family/{id}", response_model=Optional[schemas.Family], tags=[Tag.FAMILY])
def get_family_by_id(
    id: int,
    session: Session = Depends(get_session),
) -> Optional[models.Family]:
    """Returns Family by id."""
    family: Optional[models.Family] = session.get(models.Family, id)
    return family


# get families by specified [offset, limit]
@app.get("/families/", response_model=list[schemas.Family], tags=[Tag.FAMILY])
def get_families(
    offset: int = 0,
    limit: Annotated[int, Query(le=10)] = 3,
    session: Session = Depends(get_session),
) -> list[models.Family]:
    """Returns Families with limit and offset."""
    families: list[models.Family] = (
        session.query(models.Family).offset(offset).limit(limit).all()
    )
    return families


# tag: Genus
# ========================
@app.post(path="/genus/create/", response_model=schemas.Genus, tags=[Tag.GENUS])
def create_genus(
    genus_create: schemas.GenusCreate, session: Session = Depends(get_session)
) -> models.Genus:
    """Creates a new genus in the database.

    The id of the genus is autoincrement. If a genus with the same name
    already exists, the existing genus is returned.
    """
    existing_genus: models.Genus | None = (
        session.query(models.Genus).filter_by(name=genus_create.name).first()
    )
    family = dbm.get_or_create(
        session=session, model=models.Family, name=genus_create.family_name
    )
    if existing_genus:
        genus: models.Genus = existing_genus
    else:
        # update Genus
        new_genus = models.Genus(name=genus_create.name, family_id=family.id)
        session.add(new_genus)
        session.commit()
        session.refresh(new_genus)
        genus: models.Genus = new_genus
    return genus


@app.get("/genus/{id}", response_model=Optional[schemas.Genus], tags=[Tag.GENUS])
def get_genus_by_id(
    id: int,
    session: Session = Depends(get_session),
) -> Optional[models.Genus]:
    """Returns Genus by id."""
    genus: Optional[models.Genus] = session.get(models.Genus, id)
    return genus


@app.get("/genus/", response_model=list[schemas.Genus], tags=[Tag.GENUS])
def get_genus(
    offset: int = 0,
    limit: Annotated[int, Query(le=10)] = 3,
    session: Session = Depends(get_session),
) -> list[models.Genus]:
    """Returns Genus with limit and offset."""
    genus: list[models.Genus] = (
        session.query(models.Genus).offset(offset).limit(limit).all()
    )
    return genus


# tag: Species
# ========================
@app.post(path="/species/create/", response_model=schemas.Species, tags=[Tag.SPECIES])
def create_species(
    species_create: schemas.SpeciesCreate, session: Session = Depends(get_session)
) -> models.Species:
    """Creates a new species in the database.

    The id of the species is autoincrement. If a species with the same name
    already exists, the existing species is returned.
    """
    existing_species: models.Species | None = (
        session.query(models.Species).filter_by(name=species_create.name).first()
    )
    genus = dbm.get_or_create(
        session=session, model=models.Genus, name=species_create.genus_name
    )

    if existing_species:
        species: models.Species = existing_species
    else:
        # update Species
        new_species = models.Species(name=species_create.name, genus_id=genus.id)
        session.add(new_species)
        session.commit()
        session.refresh(new_species)
        species: models.Species = new_species
    return species


@app.get("/species/{id}", response_model=Optional[schemas.Species], tags=[Tag.SPECIES])
def get_species_by_id(
    id: int,
    session: Session = Depends(get_session),
) -> Optional[models.Species]:
    """Returns Species by id."""
    species: Optional[models.Species] = session.get(models.Species, id)
    return species


@app.get("/species/", response_model=List[schemas.Species], tags=[Tag.SPECIES])
def get_species(
    offset: int = 0,
    limit: Annotated[int, Query(le=10)] = 3,
    session: Session = Depends(get_session),
) -> list[models.Species]:
    """Returns Species with limit and offset."""
    species: list[models.Species] = (
        session.query(models.Species).offset(offset).limit(limit).all()
    )
    return species


# tag: Area
# ========================
@app.post(path="/area/create/", response_model=schemas.Area, tags=[Tag.AREA])
def create_area(
    area_create: schemas.AreaCreate, session: Session = Depends(get_session)
) -> models.Area:
    """Creates a new area in the database.

    The id of the area is autoincrement. If a area with the same name
    already exists, the existing area is returned.
    """
    existing_area: models.Area | None = (
        session.query(models.Area).filter_by(name=area_create.name).first()
    )
    if existing_area:
        area: models.Area = existing_area
    else:
        new_area = models.Area(name=area_create.name, code=area_create.code)
        session.add(new_area)
        session.commit()
        session.refresh(new_area)
        area: models.Area = new_area
    return area


@app.get("/area/{id}", response_model=Optional[schemas.Area], tags=[Tag.AREA])
def get_area_by_id(
    id: int,
    session: Session = Depends(get_session),
) -> Optional[models.Area]:
    """Returns Area by id."""
    area: Optional[models.Area] = session.get(models.Area, id)
    return area


@app.get("/areas/", response_model=List[schemas.Area], tags=[Tag.AREA])
def get_areas(
    offset: int = 0,
    limit: Annotated[int, Query(le=10)] = 3,
    session: Session = Depends(get_session),
) -> list[models.Area]:
    """Returns Areas with limit and offset."""
    areas: list[models.Area] = (
        session.query(models.Area).offset(offset).limit(limit).all()
    )
    return areas


# tag: Region
# ========================
@app.post(path="/region/create/", response_model=schemas.Region, tags=[Tag.REGION])
def create_region(
    region_create: schemas.RegionCreate, session: Session = Depends(get_session)
) -> models.Region:
    """Creates a new region in the database.

    The id of the region is autoincrement. If a region with the same name
    already exists, the existing region is returned.
    """
    existing_region: models.Region | None = (
        session.query(models.Region).filter_by(name=region_create.name).first()
    )
    if existing_region:
        region: models.Region = existing_region
    else:
        new_region = models.Region(name=region_create.name, code=region_create.code)
        session.add(new_region)
        session.commit()
        session.refresh(new_region)
        region: models.Region = new_region
    return region


@app.get("/region/{id}", response_model=Optional[schemas.Region], tags=[Tag.REGION])
def get_region_by_id(
    id: int, session: Session = Depends(get_session)
) -> Optional[models.Region]:
    """Returns Region by id."""
    region: Optional[models.Region] = session.get(models.Region, id)
    return region


@app.get("/regions/", response_model=List[schemas.Region], tags=[Tag.REGION])
def get_regions(
    offset: int = 0,
    limit: Annotated[int, Query(le=10)] = 3,
    session: Session = Depends(get_session),
) -> list[models.Region]:
    """Returns Regions with limit and offset."""
    regions: list[models.Region] = (
        session.query(models.Region).offset(offset).limit(limit).all()
    )
    return regions


# tag: Continent
# ========================


@app.post(
    path="/continent/create/", response_model=schemas.Continent, tags=[Tag.CONTINENT]
)
def create_continent(
    continent_create: schemas.ContinentCreate, session: Session = Depends(get_session)
) -> models.Continent:
    """Creates a new continent in the database.

    The id of the continent is autoincrement. If a continent with the same name
    already exists, the existing continent is returned.
    """
    existing_continent: models.Continent | None = (
        session.query(models.Continent).filter_by(name=continent_create.name).first()
    )
    if existing_continent:
        continent: models.Continent = existing_continent
    else:
        new_continent = models.Continent(
            name=continent_create.name, code=continent_create.code
        )
        session.add(new_continent)
        session.commit()
        session.refresh(new_continent)
        continent: models.Continent = new_continent
    return continent


@app.get(
    "/continent/{id}", response_model=Optional[schemas.Continent], tags=[Tag.CONTINENT]
)
def get_continent_by_id(
    id: int, session: Session = Depends(get_session)
) -> Optional[models.Continent]:
    """Returns Continent by id."""
    continent: Optional[models.Continent] = session.get(models.Continent, id)
    return continent


@app.get("/continents/", response_model=List[schemas.Continent], tags=[Tag.CONTINENT])
def get_continents(
    offset: int = 0,
    limit: Annotated[int, Query(le=10)] = 3,
    session: Session = Depends(get_session),
) -> list[models.Continent]:
    """Returns Continents with limit and offset."""
    continents: list[models.Continent] = (
        session.query(models.Continent).offset(offset).limit(limit).all()
    )
    return continents


# tag: Geographoic Area
# ========================


@app.get(
    "/geographic_areas/",
    response_model=List[schemas.Geographic_Area],
    tags=[Tag.GEOGRAPHIC_AREA],
)
def get_geographic_areas(
    offset: int = 0,
    limit: Annotated[int, Query(le=10)] = 3,
    session: Session = Depends(get_session),
) -> list[models.GeographicArea]:
    """Returns Continents with limit and offset."""
    geo_areas: list[models.GeographicArea] = (
        session.query(models.GeographicArea).offset(offset).limit(limit).all()
    )
    return geo_areas


# tag: Climate
# ========================


@app.post(path="/climate/create/", response_model=schemas.Climate, tags=[Tag.CLIMATE])
def create_climate(
    climate_create: schemas.ClimateCreate, session: Session = Depends(get_session)
) -> models.ClimateDescription:
    """Creates a new climate in the database.

    The id of the climate is autoincrement. If a climate with the same name
    already exists, the existing climate is returned.
    """
    existing_climate: models.ClimateDescription | None = (
        session.query(models.ClimateDescription)
        .filter_by(decription=climate_create.description)
        .first()
    )
    if existing_climate:
        climate: models.ClimateDescription = existing_climate
    else:
        new_climate = models.ClimateDescription(description=climate_create.description)
        session.add(new_climate)
        session.commit()
        session.refresh(new_climate)
        climate: models.ClimateDescription = new_climate
    return climate


@app.get("/climate/{id}", response_model=Optional[schemas.Climate], tags=[Tag.CLIMATE])
def get_climate_by_id(
    id: int, session: Session = Depends(get_session)
) -> Optional[models.ClimateDescription]:
    """Returns Climate by id."""
    climate: Optional[models.ClimateDescription] = session.get(
        models.ClimateDescription, id
    )
    return climate


@app.get("/climates/", response_model=List[schemas.Climate], tags=[Tag.CLIMATE])
def get_climates(
    offset: int = 0,
    limit: Annotated[int, Query(le=10)] = 3,
    session: Session = Depends(get_session),
) -> list[models.ClimateDescription]:
    """Returns Climates with limit and offset."""
    climates: list[models.ClimateDescription] = (
        session.query(models.ClimateDescription).offset(offset).limit(limit).all()
    )
    return climates


# tag: LifeForm
# ========================


@app.post(
    path="/life_form/create/", response_model=schemas.LifeForm, tags=[Tag.LIFEFORM]
)
def create_life_form(
    life_form_create: schemas.LifeFormCreate, session: Session = Depends(get_session)
) -> models.LifeFormDescription:
    """Creates a new life form in the database.

    The id of the life form is autoincrement. If a life form with the same name
    already exists, the existing life form is returned.
    """
    existing_life_form: models.LifeFormDescription | None = (
        session.query(models.LifeFormDescription)
        .filter_by(description=life_form_create.description)
        .first()
    )
    if existing_life_form:
        life_form: models.LifeFormDescription = existing_life_form
    else:
        new_life_form = models.LifeFormDescription(
            description=life_form_create.description
        )
        session.add(new_life_form)
        session.commit()
        session.refresh(new_life_form)
        life_form: models.LifeFormDescription = new_life_form
    return life_form


@app.get(
    path="/life_forms/", response_model=list[schemas.LifeForm], tags=[Tag.LIFEFORM]
)
def get_life_forms(
    offset: int = 0,
    limit: Annotated[int, Query(le=10)] = 3,
    session: Session = Depends(get_session),
) -> list[models.LifeFormDescription]:
    """Returns Climates with limit and offset."""
    lifeforms: list[models.LifeFormDescription] = (
        session.query(models.LifeFormDescription).offset(offset).limit(limit).all()
    )
    return lifeforms


# tag: Taxon
# ========================
@app.post(path="/taxon/create/", response_model=schemas.Taxon, tags=[Tag.TAXON])
def create_taxon(
    taxon_create: schemas.TaxonCreate, session: Session = Depends(get_session)
) -> models.Taxon:
    """Creates a new taxon in the database.

    The id of the taxon is autoincrement. If a taxon with the same name
    already exists, the existing taxon is returned.
    """

    # create Taxon foreign keys if not exist
    taxon_rank = dbm.get_or_create(
        session=session,
        model=models.TaxonRank,
        rank=taxon_create.taxon_rank.lower().title(),
    )
    taxon_status = dbm.get_or_create(
        session=session,
        model=models.TaxonStatus,
        status=taxon_create.taxon_status.lower().title(),
    )

    # check if taxon exist
    existing_taxon: models.Taxon | None = (
        session.query(models.Taxon)
        .filter_by(taxon_name=taxon_create.taxon_name)
        .first()
    )
    if existing_taxon:
        taxon: models.Taxon = existing_taxon

    else:
        new_taxon = models.Taxon(
            taxon_name=taxon_create.taxon_name,
            # foreign keys
            rank_id=taxon_rank.id,
            status_id=taxon_status.id,
        )

        session.add(new_taxon)
        session.commit()
        session.refresh(new_taxon)
        taxon: models.Taxon = new_taxon
    return taxon


@app.get(
    "/taxon/{taxon_name}", response_model=Optional[schemas.Taxon], tags=[Tag.TAXON]
)
def get_taxon_by_name(name: str, session: Session = Depends(get_session)):
    """Returns Taxon by taxon_name."""

    taxon = session.query(models.Taxon).filter_by(taxon_name=name).first()
    if not taxon:
        raise HTTPException(status_code=404, detail="Taxon not found")
    return taxon


@app.delete(
    "/taxon/{taxon_name}", response_model=Optional[schemas.Taxon], tags=[Tag.TAXON]
)
def delete_taxon_by_id(name: str, session: Session = Depends(get_session)):

    taxon = session.query(models.Taxon).filter_by(taxon_name=name).first()
    # check existing of item
    if not taxon:
        return JSONResponse(content=False, status_code=404)

    # Delete the taxon
    session.delete(taxon)
    session.commit()

    return JSONResponse(content=True)


@app.get("/taxons/", response_model=list[schemas.Taxon], tags=[Tag.TAXON])
def get_taxons(
    offset: int = 0,
    limit: Annotated[int, Query(le=10)] = 3,
    session: Session = Depends(get_session),
) -> list[models.Taxon]:
    """Returns Taxons with limit and offset."""
    taxons: list[models.Taxon] = (
        session.query(models.Taxon).offset(offset).limit(limit).all()
    )
    return taxons


@app.get("/taxons/by_taxon_rank/", response_model=list[schemas.Taxon], tags=[Tag.TAXON])
def get_taxons_by_taxon_rank(taxon_rank: str, session: Session = Depends(get_session)):
    # Look up the taxon_rank ID using the taxon_rank
    taxon_rank = taxon_rank.lower().title()
    rank = session.query(models.TaxonRank).filter_by(rank=taxon_rank).first()

    if not rank:
        raise HTTPException(
            status_code=404,
            detail="taxon_rank not found. Accepted ranks include Convariety, Form, Genus, proles, Species, Subform, Subspecies, Subvariety, Variety",
        )

    # Get taxons by taxon_rank_id
    taxons = session.query(models.Taxon).filter_by(rank_id=rank.id).all()

    return taxons


@app.get(
    "/taxons/by_taxon_status/", response_model=list[schemas.Taxon], tags=[Tag.TAXON]
)
def get_taxons_by_taxon_status(
    taxon_status: str = Query(..., description="Status of the taxon"),
    session: Session = Depends(get_session),
):
    # Look up the taxon_status ID using the taxon status
    taxon_status = taxon_status.lower().title()
    status = session.query(models.TaxonStatus).filter_by(status=taxon_status).first()

    if not status:
        raise HTTPException(
            status_code=404,
            detail="Taxon Status not found. Accepted status includes:Accepted, Artificial Hybrid, Illegitimate, Invalid, Local Biotype, Misapplied, Orthographic, Synonym, Unplaced, Provisionally Accepted ",
        )

    # Get taxons by status id
    taxons = session.query(models.Taxon).filter_by(status_id=status.id).all()

    return taxons


# tag: Plant
# ========================


@app.post(path="/plant/create/", response_model=schemas.Plant, tags=[Tag.PLANT])
def create_plant(
    plant_create: schemas.PlantCreate, session: Session = Depends(get_session)
) -> models.Plant:
    """Creates a new plant in the database.

    The id of the plant is autoincrement. If a plant with the same plant_name_id
    already exists, the existing plant is returned.
    """

    # create Plant foreign keys if not exist
    taxon_rank = dbm.get_or_create(
        session=session, model=models.TaxonRank, rank=plant_create.taxon_rank
    )
    taxon_status = dbm.get_or_create(
        session=session, model=models.TaxonStatus, status=plant_create.taxon_status
    )
    taxon = dbm.get_or_create(
        session=session,
        model=models.Taxon,
        taxon_name=plant_create.taxon_name,
        rank_id=taxon_rank.id,
        status_id=taxon_status.id,
    )

    family = dbm.get_or_create(
        session=session, model=models.Family, name=plant_create.family_name
    )

    genus = dbm.get_or_create(
        session=session,
        model=models.Genus,
        name=plant_create.genus_name,
        family_id=family.id,
    )

    species = dbm.get_or_create(
        session=session,
        model=models.Species,
        name=plant_create.species_name,
        genus_id=genus.id,
    )

    publication = dbm.get_or_create(
        session=session,
        model=models.Publication,
        primary_author=plant_create.primary_author_name,
        first_published=datetime.strptime(
            plant_create.first_published, "%Y-%m-%d"
        ).date(),
    )
    area = dbm.get_or_create(
        session=session,
        model=models.Area,
        code=plant_create.area_code,
        name=plant_create.area_name,
    )
    region = dbm.get_or_create(
        session=session,
        model=models.Region,
        code=plant_create.region_code,
        name=plant_create.region_name,
    )
    continent = dbm.get_or_create(
        session=session,
        model=models.Continent,
        code=plant_create.continent_code,
        name=plant_create.continent_name,
    )
    geo_area = dbm.get_or_create(
        session=session,
        model=models.GeographicArea,
        name=plant_create.geographic_area_name,
        area_id=area.id,
        region_id=region.id,
        continent_id=continent.id,
    )
    lifeform = dbm.get_or_create(
        session=session,
        model=models.LifeFormDescription,
        description=plant_create.lifeform_description,
    )
    climate = dbm.get_or_create(
        session=session,
        model=models.ClimateDescription,
        description=plant_create.climate_description,
    )
    environment = dbm.get_or_create(
        session=session,
        model=models.EnvironmentalDescription,
        lifeform_id=lifeform.id,
        climate_id=climate.id,
    )

    infraspecies = dbm.get_or_create(
        session=session, model=models.InfraSpecies, name=plant_create.infraspecies_name
    )

    # check if taxon exist
    existing_plant: models.Taxon | None = (
        session.query(models.Plant)
        .filter_by(plant_name_id=plant_create.plant_name_id)
        .first()
    )
    if existing_plant:
        plant: models.Plant = existing_plant

    else:
        new_plant = models.Plant(
            plant_name_id=plant_create.plant_name_id,
            reviewed=(plant_create.reviewed == "Y"),
            ipni_id=plant_create.ipni_id,
            introduced=(plant_create.introduced == "Y"),
            extinct=(plant_create.extinct == "Y"),
            location_doubtful=(plant_create.location_doubtful == "Y"),
            # foreign keys
            taxon_id=taxon.id,
            family_id=family.id,
            genus_id=genus.id,
            species_id=species.id,
            publication_id=publication.id,
            geographic_area_id=geo_area.id,
            environmental_description_id=environment.id,
            infraspecies_id=infraspecies.id,
        )
        session.add(new_plant)
        session.commit()
        session.refresh(new_plant)

        plant: models.Plant = new_plant
    return plant


@app.get(
    "/plant/{plant_name_id}", response_model=Optional[schemas.Plant], tags=[Tag.PLANT]
)
def get_plant_by_id(plant_name_id: int, session: Session = Depends(get_session)):
    """Returns plant by id."""

    plant = session.query(models.Plant).filter_by(plant_name_id=plant_name_id).first()
    if not plant:
        raise HTTPException(status_code=404, detail="Plant not found")
    return plant


@app.delete(
    "/plant/{plant_name_id}", response_model=Optional[schemas.Plant], tags=[Tag.PLANT]
)
def delete_plant_by_id(plant_name_id: int, session: Session = Depends(get_session)):

    plant = session.query(models.Plant).filter_by(plant_name_id=plant_name_id).first()
    # check existing of item
    if not plant:
        return JSONResponse(content=False, status_code=404)

    # Delete the taxon
    session.delete(plant)
    session.commit()

    return JSONResponse(content=True)


@app.get("/plants/", response_model=list[schemas.Plant], tags=[Tag.PLANT])
def get_plants(
    offset: int = 0,
    limit: Annotated[int, Query(le=10)] = 3,
    session: Session = Depends(get_session),
) -> list[models.Plant]:
    """Returns Plants with limit and offset."""
    plants: list[models.Plant] = (
        session.query(models.Plant).offset(offset).limit(limit).all()
    )
    return plants


@app.get("/plants/by_family/", response_model=list[schemas.Plant], tags=[Tag.PLANT])
def get_plants_by_family(
    name: str = Query(..., description="Name of the family"),
    session: Session = Depends(get_session),
):
    # Look up the family ID using the family name
    family = session.query(models.Family).filter_by(name=name).first()

    if not family:
        raise HTTPException(status_code=404, detail="Family not found")

    # Get plants by family id
    plants = session.query(models.Plant).filter_by(family_id=family.id).all()

    return plants


@app.get("/plants/by_genus/", response_model=list[schemas.Plant], tags=[Tag.PLANT])
def get_plants_by_genus(
    name: str = Query(..., description="Name of the genus"),
    session: Session = Depends(get_session),
):
    # Look up the genus ID using the genus name
    genus = session.query(models.Genus).filter_by(name=name).first()

    if not genus:
        raise HTTPException(status_code=404, detail="Genus not found")

    # Get taxons by family id
    plants = session.query(models.Plant).filter_by(genus_id=genus.id).all()

    return plants


@app.get("/plants/by_species/", response_model=list[schemas.Plant], tags=[Tag.PLANT])
def get_plants_by_species(
    name: str = Query(..., description="Name of the species"),
    session: Session = Depends(get_session),
):
    # Look up the species ID using the species name
    species = session.query(models.Species).filter_by(name=name).first()

    if not species:
        raise HTTPException(status_code=404, detail="Species not found")

    # Get taxons by family id
    plants = session.query(models.Plant).filter_by(species_id=species.id).all()

    return plants


@app.get("/plants/by_extinction/", response_model=List[schemas.Plant], tags=[Tag.PLANT])
def get_plants_by_extinction(
    extinction: bool = Query(..., description="Filter by extinction status"),
    session: Session = Depends(get_session),
):
    # Get taxons by extinction
    plants = (
        session.query(models.Plant).filter(models.Plant.extinct == extinction).all()
    )
    return plants


@app.get("/plants/by_climate/", response_model=list[schemas.Plant], tags=[Tag.PLANT])
def get_plants_by_climate(
    description: str = Query(..., description="Description of the Climate"),
    session: Session = Depends(get_session),
):
    # Look up the climate ID using the climate description
    climate = (
        session.query(models.ClimateDescription)
        .filter_by(description=description)
        .first()
    )

    if not climate:
        raise HTTPException(
            status_code=404,
            detail="Climate description not found. Accepted climate includes: Desert and Dry Shrubland, Desert or Dry Shrubland, Montane Tropical, Seasonally Dry Tropical, Subalpine or Subarctic, Subtropical, Subtropical and Tropical, Temperate, Temperate and Tropical, Wet Tropical",
        )
    environment = (
        session.query(models.EnvironmentalDescription)
        .filter_by(climate_id=climate.id)
        .all()
    )

    # Get plants by environment id
    plants = []
    for env in environment:
        plant = (
            session.query(models.Plant)
            .filter_by(environmental_description_id=env.id)
            .all()
        )
        plants.extend(plant)

    return plants


@app.get("/plants/by_lifeform/", response_model=list[schemas.Plant], tags=[Tag.PLANT])
def get_plants_by_lifeform(
    descrition: str = Query(..., description="Description of the Lifeform"),
    session: Session = Depends(get_session),
):
    # Look up the lifeform ID using the lifeform description
    lifeform = (
        session.query(models.LifeFormDescription)
        .filter_by(descrition=descrition)
        .first()
    )

    if not lifeform:
        raise HTTPException(status_code=404, detail="Lifeform not found.")

    environment = (
        session.query(models.EnvironmentalDescription)
        .filter_by(lifeform_id=lifeform.id)
        .all()
    )

    # Get plants by environment id
    plants = []
    for env in environment:
        plant = (
            session.query(models.Plant)
            .filter_by(environmental_description_id=env.id)
            .all()
        )
        plants.extend(plant)
    return plants


@app.get("/plants/by_area/", response_model=list[schemas.Plant], tags=[Tag.PLANT])
def get_plants_by_area(
    name: str = Query(..., description="Name of the area"),
    session: Session = Depends(get_session),
):
    # Look up the area ID using the area name
    name = name.lower().title()
    area = session.query(models.Area).filter_by(name=name).first()

    if not area:
        raise HTTPException(status_code=404, detail="Area not found.")

    # get geographic_area id using cotinent id
    geo_area = session.query(models.GeographicArea).filter_by(area_id=area.id).all()

    # Get taxons by geo_area id
    plants = []
    for geo in geo_area:
        plant = session.query(models.Plant).filter_by(geographic_area_id=geo.id).all()
        plants.extend(plant)

    return plants


@app.get("/plants/by_region/", response_model=list[schemas.Plant], tags=[Tag.PLANT])
def get_plants_by_region(
    name: str = Query(..., description="Name of the region"),
    session: Session = Depends(get_session),
):
    # Look up the area ID using the area name
    name = name.lower().title()
    region = session.query(models.Region).filter_by(name=name).first()

    if not region:
        raise HTTPException(status_code=404, detail="Region not found.")

    # get geographic_area id using cotinent id
    geo_area = session.query(models.GeographicArea).filter_by(region_id=region.id).all()

    # Get taxons by geo_area id
    plants = []
    for geo in geo_area:
        plant = session.query(models.Plant).filter_by(geographic_area_id=geo.id).all()
        plants.extend(plant)

    return plants


@app.get("/plants/by_continent/", response_model=List[schemas.Plant], tags=[Tag.PLANT])
def get_plants_by_continent(
    name: str = Query(..., description="Name of the continent"),
    session: Session = Depends(get_session),
):
    # Look up the continent ID using the continent name
    name = name.upper()
    continent = session.query(models.Continent).filter_by(name=name).first()

    if not continent:
        raise HTTPException(status_code=404, detail="Continent not found.")

    # Get geographic_area IDs using continent ID
    geo_areas = (
        session.query(models.GeographicArea).filter_by(continent_id=continent.id).all()
    )

    # Get taxons by geographic_area IDs
    plants = []
    for geo in geo_areas:
        plant_instances = (
            session.query(models.Plant).filter_by(geographic_area_id=geo.id).all()
        )
        plants.extend(
            plant_instances
        )  # Use extend instead of append to flatten the list

    # Convert SQLAlchemy models to Pydantic models
    # return [schemas.Taxon.from_orm(taxon) for taxon in taxons]
    return plants
