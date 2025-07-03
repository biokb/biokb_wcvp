import logging
import os
import secrets
from contextlib import asynccontextmanager
from typing import Annotated, Dict, Optional

from fastapi import Depends, FastAPI, HTTPException, Query, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from biokb_wcvp.api import schemas
from biokb_wcvp.api.query_tools import build_dynamic_query
from biokb_wcvp.api.tags import Tag
from biokb_wcvp.db import manager, models

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

USERNAME = os.environ.get("API_USERNAME", "admin")
PASSWORD = os.environ.get("API_PASSWORD", "admin")


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
    version="0.0.1",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
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
) -> dict[str, int]:
    """Load a tsv file in database."""
    dbm = manager.DbManager()
    return dbm.import_data()


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
    response_model=list[schemas.Contient],
    tags=[Tag.LOCATION],
)
async def search_continents(
    continent_code_l1: Optional[int] = None,
    continent: Optional[str] = None,
    session: Session = Depends(get_session),
):
    """
    Search continents.
    """
    query = session.query(
        models.Location.continent, models.Location.continent_code_l1
    ).group_by(models.Location.continent, models.Location.continent_code_l1)
    if continent_code_l1:
        query = query.filter(models.Location.continent_code_l1 == continent_code_l1)
    if continent:
        query = query.filter(models.Location.continent.like(continent))
    return query.all()


@app.get(
    "/locations/region/",
    response_model=list[schemas.Region],
    tags=[Tag.LOCATION],
)
async def search_regions(
    region_code_l2: Optional[int] = None,
    region: Optional[str] = None,
    session: Session = Depends(get_session),
):
    """
    Search regions.
    """
    query = session.query(
        models.Location.region, models.Location.region_code_l2
    ).group_by(models.Location.region, models.Location.region_code_l2)
    if region_code_l2:
        query = query.filter(models.Location.region_code_l2 == region_code_l2)
    if region:
        query = query.filter(models.Location.region.like(region))
    return query.all()


@app.get(
    "/locations/area/",
    response_model=list[schemas.Area],
    tags=[Tag.LOCATION],
)
async def search_areas(
    area_code_l3: Optional[int] = None,
    area: Optional[str] = None,
    session: Session = Depends(get_session),
):
    """
    Search areas.
    """
    query = session.query(models.Location.area, models.Location.area_code_l3).group_by(
        models.Location.area, models.Location.area_code_l3
    )
    if area_code_l3:
        query = query.filter(models.Location.area_code_l3 == area_code_l3)
    if area:
        query = query.filter(models.Location.area.like(area))
    return query.all()


@app.get(
    "/plant_location/",
    response_model=schemas.PlantLocationSearchResults,
    tags=[Tag.LOCATION, Tag.PLANT],
)
async def search_plant_location(
    offset: int = 0,
    limit: Annotated[int, Query(le=100)] = 10,
    wcvp_id: Optional[int] = None,
    ipni_id: Optional[str] = None,
    family: Optional[str] = None,
    taxon_name: Optional[str] = None,
    taxon_rank: Optional[str] = None,
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
            models.Plant.id.label("plant_id"),
            models.Plant.ipni_id,
            models.Plant.family,
            models.Plant.taxon_name,
            models.Plant.taxon_rank,
            models.Plant.powo_id,
            models.Location.continent,
            models.Location.region,
            models.Location.area,
            models.Location.area_code_l3,
        )
        .select_from(models.Plant)
        .join(models.Location)
    )
    stmt = stmt.group_by(
        models.Plant.id,
        models.Plant.ipni_id,
        models.Plant.family,
        models.Plant.taxon_name,
        models.Plant.taxon_rank,
        models.Plant.powo_id,
        models.Location.continent,
        models.Location.region,
        models.Location.area,
        models.Location.area_code_l3,
    )
    if wcvp_id:
        stmt = stmt.filter(models.Plant.id == wcvp_id)
    if ipni_id:
        stmt = stmt.filter(models.Plant.ipni_id == ipni_id)
    if family:
        stmt = stmt.filter(models.Plant.family.like(family))
    if taxon_name:
        stmt = stmt.filter(models.Plant.taxon_name.like(taxon_name))
    if taxon_rank:
        stmt = stmt.filter(models.Plant.taxon_rank.like(taxon_rank))
    if powo_id:
        stmt = stmt.filter(models.Plant.powo_id.like(powo_id))
    if continent:
        stmt = stmt.filter(models.Location.continent.like(continent))
    if region:
        stmt = stmt.filter(models.Location.region.like(region))
    if area:
        stmt = stmt.filter(models.Location.area.like(area))

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
    plant_id: Optional[int] = None,
    ipni_id: Optional[str] = None,
    taxon_name: Optional[str] = None,
    powo_id: Optional[str] = None,
    session: Session = Depends(get_session),
):
    """
    Search plant and location in one step.
    """
    if not any([plant_id, ipni_id, taxon_name, powo_id]):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="At least one query parameter (plant_id, ipni_id, taxon_name, powo_id) must be provided.",
        )
    stmt = (
        select(func.count().label("species_count"), models.Location.area_code_l3)
        .select_from(models.Plant)
        .join(models.Location)
    )
    if plant_id:
        stmt = stmt.filter(models.Plant.id == plant_id)
    if ipni_id:
        stmt = stmt.filter(models.Plant.ipni_id == ipni_id)
    if taxon_name:
        stmt = stmt.filter(models.Plant.taxon_name.like(taxon_name))
    if powo_id:
        stmt = stmt.filter(models.Plant.powo_id == powo_id)
    stmt = stmt.group_by(models.Location.area_code_l3)
    return session.execute(stmt)
