import logging
import os
import secrets
from contextlib import asynccontextmanager
from typing import Annotated, Dict, Optional

import uvicorn
from fastapi import Depends, FastAPI, HTTPException, Query, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from biokb_wcvp.api import schemas
from biokb_wcvp.api.query_tools import build_dynamic_query
from biokb_wcvp.api.tags import Tag
from biokb_wcvp.constants import ZIPPED_TTLS_PATH
from biokb_wcvp.db import manager, models
from biokb_wcvp.rdf.neo4j_importer import Neo4jImporter
from biokb_wcvp.rdf.turtle import TurtleCreator

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

USERNAME = os.environ.get("WCVP_API_USERNAME", "admin")
PASSWORD = os.environ.get("WCVP_API_PASSWORD", "admin")


def get_session():
    with manager.DbManager().Session() as session:
        yield session


@asynccontextmanager
async def lifespan(app: FastAPI):
    # dbm.drop_db()
    dbm = manager.DbManager()
    yield
    # Clean up
    pass


description = """A RESTful API for WCVP."""

app = FastAPI(
    title="RESTful API for WCVP",
    description=description,
    version="0.1.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)


def run_api(host: str = "0.0.0.0", port: int = 8000):
    uvicorn.run(
        app="biokb_wcvp.api.main:app",
        host=host,
        port=port,
        log_level="warning",
    )


def verify_credentials(credentials: HTTPBasicCredentials = Depends(HTTPBasic())):
    is_correct_username = secrets.compare_digest(credentials.username, USERNAME)
    is_correct_password = secrets.compare_digest(credentials.password, PASSWORD)
    if not (is_correct_username and is_correct_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
            headers={"WWW-Authenticate": "Basic"},
        )


# tag: Database Management
# ========================


@app.post(path="/import_data/", response_model=dict[str, int], tags=[Tag.DBMANAGE])
def import_data(
    credentials: HTTPBasicCredentials = Depends(verify_credentials),
) -> Dict[str, int]:
    """Download data and import it into the database."""
    dbm = manager.DbManager()
    return dbm.import_data()


@app.get(path="/download_ttls/", tags=[Tag.DBMANAGE])
async def export_ttls(
    credentials: HTTPBasicCredentials = Depends(verify_credentials),
) -> FileResponse:
    """Create zipped RDF turtle files (if not exists) for WCVP data export."""
    dbm = manager.DbManager()
    if not os.path.exists(ZIPPED_TTLS_PATH):
        tc = TurtleCreator(dbm.__engine)
        tc.create_ttls()

    return FileResponse(
        path=ZIPPED_TTLS_PATH, filename="wcvp_ttls.zip", media_type="application/zip"
    )


@app.get(path="/import_into_neo4j/", tags=[Tag.DBMANAGE])
async def import_into_neo4j(
    credentials: HTTPBasicCredentials = Depends(verify_credentials),
):
    """Create zipped RDF turtle files (if not exists) for WCVP data export."""
    dbm = manager.DbManager()
    # check if database exists and has data
    plant_table_exists = dbm.__engine.dialect.has_table(
        dbm.__engine.connect(), models.Plant.__tablename__
    )
    if not plant_table_exists:
        dbm.import_data()
    else:
        with dbm.Session() as session:
            result = session.query(models.Plant).count()
            if result == 0:
                dbm.import_data()

    if not os.path.exists(ZIPPED_TTLS_PATH):
        tc = TurtleCreator(dbm.__engine)
        tc.create_ttls()

    ni = Neo4jImporter()
    ni.import_ttls(delete_existing_graph=True)

    return True


@app.get(
    "/plants/",
    response_model=schemas.PlantSearchResults,
    tags=[Tag.PLANT],
)
async def search_plants(
    search: schemas.PlantSearch = Depends(),
    offset: int = 0,
    limit: Annotated[int, Query(le=100)] = 10,
    session: Session = Depends(get_session),
):
    """
    Search plants.
    """
    return build_dynamic_query(
        search_obj=search,
        model_cls=models.Plant,
        db=session,
        limit=limit,
        offset=offset,
    )


@app.get(
    "/plants/with_locations/",
    response_model=schemas.PlantSearchResultsWithLocs,
    tags=[Tag.PLANT],
)
async def search_plants_with_locations(
    search: schemas.PlantSearch = Depends(),
    offset: int = 0,
    limit: Annotated[int, Query(le=100)] = 10,
    session: Session = Depends(get_session),
):
    """
    Search plants.
    """
    return build_dynamic_query(
        search_obj=search,
        model_cls=models.Plant,
        db=session,
        limit=limit,
        offset=offset,
    )


@app.get(
    "/locations/", response_model=schemas.LocationSearchResults, tags=[Tag.LOCATION]
)
async def search_locations(
    search: schemas.LocationSearch = Depends(),
    offset: int = 0,
    limit: Annotated[int, Query(le=100)] = 10,
    session: Session = Depends(get_session),
):
    """
    Search locations.
    """
    return build_dynamic_query(
        search_obj=search,
        model_cls=models.Location,
        db=session,
        limit=limit,
        offset=offset,
    )


@app.get(
    "/locations/continent/",
    response_model=list[schemas.Continent],
    tags=[Tag.LOCATION],
)
async def search_continents(
    code_l1: Optional[int] = None,
    name: Optional[str] = None,
    session: Session = Depends(get_session),
):
    """Search continents (and parts) by filtering TDWG (Biodiversity Information Standards) code_l1 and name."""
    query = session.query(models.Continent)
    if code_l1:
        query = query.filter(models.Continent.code_l1 == code_l1)
    if name:
        query = query.filter(models.Continent.name.like(name))
    return query.all()


@app.get(
    "/locations/region/",
    response_model=list[schemas.Region],
    tags=[Tag.LOCATION],
)
async def search_regions(
    code_l2: Optional[int] = None,
    name: Optional[str] = None,
    session: Session = Depends(get_session),
):
    """Search regions by filtering TDWG (Biodiversity Information Standards) code_l2 and name."""
    query = session.query(models.Region)
    if code_l2:
        query = query.filter(models.Region.code_l2 == code_l2)
    if name:
        query = query.filter(models.Region.name.like(name))
    return query.all()


@app.get(
    "/locations/area/",
    response_model=list[schemas.Area],
    tags=[Tag.LOCATION],
)
async def search_areas(
    code_l3: Optional[str] = None,
    name: Optional[str] = None,
    session: Session = Depends(get_session),
):
    """Search areas by filtering TDWG (Biodiversity Information Standards) code_l3 and name."""
    query = session.query(models.Area)
    if code_l3:
        query = query.filter(models.Area.code_l3 == code_l3)
    if name:
        query = query.filter(models.Area.name.like(name))
    return query.all()


@app.get(
    "/plant_location/",
    response_model=schemas.PlantLocationSearchResults,
    tags=[Tag.LOCATION, Tag.PLANT],
)
async def search_plant_location(
    offset: int = 0,
    limit: Annotated[int, Query(le=100)] = 10,
    plant_name_id: Optional[int] = None,
    ipni_id: Optional[str] = None,
    family: Optional[str] = None,
    taxon_name: Optional[str] = None,
    taxon_rank: Optional[str] = None,
    infraspecific_rank: Optional[str] = None,
    infraspecies: Optional[str] = None,
    powo_id: Optional[str] = None,
    continent: Optional[str] = None,
    region: Optional[str] = None,
    area: Optional[str] = None,
    session: Session = Depends(get_session),
):
    """
    Search plant and location in one step.
    """

    stmt = (
        select(
            models.Plant.plant_name_id,
            models.Plant.ipni_id,
            models.Family.name.label("family"),
            models.Plant.taxon_name,
            models.TaxonRank.name.label("taxon_rank"),
            models.InfraspecificRank.name.label("infraspecific_rank"),
            models.Plant.infraspecies,
            models.Plant.powo_id,
            models.Continent.name.label("continent"),
            models.Region.name.label("region"),
            models.Area.name.label("area"),
            models.Location.code_l3,
        )
        .select_from(models.Plant)
        .join(
            models.Location, models.Plant.plant_name_id == models.Location.wcvp_plant_id
        )
        .outerjoin(models.Family, models.Plant.family_id == models.Family.id)
        .outerjoin(models.TaxonRank, models.Plant.taxon_rank_id == models.TaxonRank.id)
        .outerjoin(
            models.InfraspecificRank,
            models.Plant.infraspecific_rank_id == models.InfraspecificRank.id,
        )
        .outerjoin(
            models.Continent, models.Location.code_l1 == models.Continent.code_l1
        )
        .outerjoin(models.Region, models.Location.code_l2 == models.Region.code_l2)
        .outerjoin(models.Area, models.Location.code_l3 == models.Area.code_l3)
    )
    stmt = stmt.group_by(
        models.Plant.plant_name_id,
        models.Plant.ipni_id,
        models.Family.name,
        models.Plant.taxon_name,
        models.TaxonRank.name,
        models.InfraspecificRank.name,
        models.Plant.infraspecies,
        models.Plant.powo_id,
        models.Continent.name,
        models.Region.name,
        models.Area.name,
        models.Location.code_l3,
    )
    if plant_name_id:
        stmt = stmt.filter(models.Plant.plant_name_id == plant_name_id)
    if ipni_id:
        stmt = stmt.filter(models.Plant.ipni_id == ipni_id)
    if family:
        stmt = stmt.filter(models.Family.name.like(family))
    if taxon_name:
        stmt = stmt.filter(models.Plant.taxon_name.like(taxon_name))
    if taxon_rank:
        stmt = stmt.filter(models.TaxonRank.name.like(taxon_rank))
    if infraspecific_rank:
        stmt = stmt.filter(models.InfraspecificRank.name.like(infraspecific_rank))
    if infraspecies:
        stmt = stmt.filter(models.Plant.infraspecies.like(infraspecies))
    if powo_id:
        stmt = stmt.filter(models.Plant.powo_id.like(powo_id))
    if continent:
        stmt = stmt.filter(models.Continent.name.like(continent))
    if region:
        stmt = stmt.filter(models.Region.name.like(region))
    if area:
        stmt = stmt.filter(models.Area.name.like(area))

    count = session.execute(
        select(func.count()).select_from(stmt.subquery())
    ).scalar_one()

    return {
        "count": count,
        "offset": offset,
        "limit": limit,
        "results": session.execute(stmt.offset(offset).limit(limit)).all(),
    }


@app.get(
    "/plant_locations_statistics/",
    response_model=list[schemas.CountryLocation],
    tags=[Tag.LOCATION, Tag.PLANT],
)
async def plant_locations_statistics(
    plant_name_id: Optional[int] = None,
    ipni_id: Optional[str] = None,
    taxon_name: Optional[str] = None,
    powo_id: Optional[str] = None,
    session: Session = Depends(get_session),
):
    """
    Get plant distribution statistics by area.
    """
    if not any([plant_name_id, ipni_id, taxon_name, powo_id]):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="At least one query parameter (plant_name_id, ipni_id, taxon_name, powo_id) must be provided.",
        )
    stmt = (
        select(func.count().label("species_count"), models.Location.code_l3)
        .select_from(models.Plant)
        .join(
            models.Location, models.Plant.plant_name_id == models.Location.wcvp_plant_id
        )
    )
    if plant_name_id:
        stmt = stmt.filter(models.Plant.plant_name_id == plant_name_id)
    if ipni_id:
        stmt = stmt.filter(models.Plant.ipni_id == ipni_id)
    if taxon_name:
        stmt = stmt.filter(models.Plant.taxon_name.like(taxon_name))
    if powo_id:
        stmt = stmt.filter(models.Plant.powo_id == powo_id)
    stmt = stmt.group_by(models.Location.code_l3)
    return session.execute(stmt)
