from enum import Enum
from itertools import count
from typing import Optional

from pydantic import BaseModel, Field


class PlantBase(BaseModel):
    """Base model for plant data."""

    id: int
    ipni_id: Optional[str] = None
    taxon_rank: Optional[str] = None
    taxon_status: str
    family: str
    genus_hybrid: Optional[str] = None
    genus: str
    species_hybrid: Optional[str] = None
    species: Optional[str] = None
    infraspecific_rank: Optional[str] = None
    infraspecies: Optional[str] = None
    parenthetical_author: Optional[str] = None
    primary_author: Optional[str] = None
    publication_author: Optional[str] = None
    place_of_publication: Optional[str] = None
    volume_and_page: Optional[str] = None
    first_published: Optional[str] = None
    nomenclatural_remarks: Optional[str] = None
    geographic_area: Optional[str] = None
    lifeform_description: Optional[str] = None
    climate_description: Optional[str] = None
    taxon_name: str
    taxon_authors: Optional[str] = None
    accepted_plant_name_id: Optional[int] = None
    basionym_plant_name_id: Optional[int] = None
    replaced_synonym_author: Optional[str] = None
    homotypic_synonym: Optional[str] = None
    parent_plant_name_id: Optional[int] = None
    powo_id: str
    hybrid_formula: Optional[str] = None
    reviewed: Optional[bool] = None


class Plant(PlantBase):
    locations: list["LocationBase"]


class PlantSearch(BaseModel):
    id: Optional[int] = None
    ipni_id: Optional[str] = None
    taxon_rank: Optional[str] = None
    taxon_status: Optional[str] = None
    family: Optional[str] = None
    genus_hybrid: Optional[str] = None
    genus: Optional[str] = None
    species_hybrid: Optional[str] = None
    species: Optional[str] = None
    infraspecific_rank: Optional[str] = None
    infraspecies: Optional[str] = None
    parenthetical_author: Optional[str] = None
    primary_author: Optional[str] = None
    publication_author: Optional[str] = None
    place_of_publication: Optional[str] = None
    volume_and_page: Optional[str] = None
    first_published: Optional[str] = None
    nomenclatural_remarks: Optional[str] = None
    geographic_area: Optional[str] = None
    lifeform_description: Optional[str] = None
    climate_description: Optional[str] = None
    taxon_name: Optional[str] = None
    taxon_authors: Optional[str] = None
    accepted_plant_name_id: Optional[int] = None
    basionym_plant_name_id: Optional[int] = None
    replaced_synonym_author: Optional[str] = None
    homotypic_synonym: Optional[str] = None
    parent_plant_name_id: Optional[int] = None
    powo_id: Optional[str] = None
    hybrid_formula: Optional[str] = None
    reviewed: Optional[bool] = None


class PlantSearchResult(BaseModel):
    count: int
    offset: int
    limit: int
    results: list[Plant]


class LocationBase(BaseModel):
    id: int
    continent_code_l1: int
    continent: str
    region_code_l2: Optional[int]
    region: Optional[str]
    area_code_l3: Optional[str]
    area: Optional[str]
    introduced: bool
    extinct: bool
    location_doubtful: bool
    wcvp_plant_id: int


class Location(LocationBase):
    plant: PlantBase


class LocationSearch(BaseModel):
    id: Optional[int] = None
    continent_code_l1: Optional[int] = None
    continent: Optional[str] = None
    region_code_l2: Optional[int] = None
    region: Optional[str] = None
    area_code_l3: Optional[str] = None
    area: Optional[str] = None
    introduced: Optional[bool] = None
    extinct: Optional[bool] = None
    location_doubtful: Optional[bool] = None
    wcvp_plant_id: Optional[int] = None


class LocationSearchResult(BaseModel):
    count: int
    offset: int
    limit: int
    results: list[Location]


class Contient(BaseModel):
    continent: Optional[str]
    continent_code_l1: Optional[int]


class Region(BaseModel):
    region: Optional[str]
    region_code_l2: Optional[int]


class Area(BaseModel):
    area: Optional[str]
    area_code_l3: Optional[str]


class PlantLocation(BaseModel):
    plant_id: int
    ipni_id: Optional[str]
    family: str
    taxon_name: str
    reviewed: Optional[bool]
    powo_id: Optional[str]
    continent: Optional[str]
    region: Optional[str]
    area: Optional[str]


class PlantLocationSearchResults(BaseModel):
    count: int
    offset: int
    limit: int
    results: list[PlantLocation]


class CountryLocation(BaseModel):
    area_code_l3: str
    species_count: int
