from enum import Enum
from itertools import count
from typing import Annotated, Any, Optional

from fastapi import Query
from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator


class PlantBase(BaseModel):
    """Base model for plant data."""

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    plant_name_id: int
    ipni_id: Optional[str] = None
    taxon_rank: Optional[str] = None  # From relationship
    taxon_status: Optional[str] = None  # From relationship
    family: Optional[str] = None  # From relationship
    genus_hybrid: Optional[str] = None
    genus: Optional[str] = None  # From relationship
    species_hybrid: Optional[str] = None
    species: Optional[str] = None
    infraspecific_rank: Optional[str] = None  # From relationship
    infraspecies: Optional[str] = None
    parenthetical_author: Optional[str] = None
    primary_author: Optional[str] = None
    publication_author: Optional[str] = None
    place_of_publication: Optional[str] = None
    volume_and_page: Optional[str] = None
    first_published: Optional[str] = None
    nomenclatural_remarks: Optional[str] = None
    geographic_area: Optional[str] = None
    lifeform_description: Optional[str] = None  # From relationship
    climate_description: Optional[str] = None  # From relationship
    taxon_name: str
    taxon_authors: Optional[str] = None
    accepted_plant_name_id: Optional[int] = None
    basionym_plant_name_id: Optional[int] = None
    replaced_synonym_author: Optional[str] = None
    homotypic_synonym: Optional[bool] = None
    parent_plant_name_id: Optional[int] = None
    powo_id: Optional[str] = None
    hybrid_formula: Optional[str] = None
    reviewed: Optional[bool] = None
    tax_id: Optional[int] = None

    @model_validator(mode="before")
    @classmethod
    def extract_relationships(cls, data: Any) -> Any:
        """Extract name fields from relationship objects."""
        if isinstance(data, dict):
            return data

        # Handle SQLAlchemy model objects
        result = {}
        for field_name in cls.model_fields.keys():
            if hasattr(data, field_name):
                value = getattr(data, field_name)
                # Handle relationship objects that have a 'name' attribute
                if hasattr(value, "name"):
                    result[field_name] = value.name
                else:
                    result[field_name] = value
        return result


class Plant(PlantBase):
    locations: list["LocationBase"]


class PlantSearch(BaseModel):
    plant_name_id: Optional[int] = None
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
    homotypic_synonym: Optional[bool] = None
    parent_plant_name_id: Optional[int] = None
    powo_id: Optional[str] = None
    hybrid_formula: Optional[str] = None
    reviewed: Optional[bool] = None
    tax_id: Optional[int] = None


class PlantSearchResultsWithLocs(BaseModel):
    count: int
    offset: int
    limit: int
    results: list[Plant]


class PlantSearchResults(BaseModel):
    count: int
    offset: int
    limit: int
    results: list[PlantBase]


class LocationBase(BaseModel):
    """Base model for location data."""

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    id: int
    code_l1: Optional[int] = None
    continent: Optional[str] = None  # From relationship
    code_l2: Optional[int] = None
    region: Optional[str] = None  # From relationship
    code_l3: Optional[str] = None
    area: Optional[str] = None  # From relationship
    introduced: bool
    extinct: bool
    location_doubtful: bool
    wcvp_plant_id: int

    @model_validator(mode="before")
    @classmethod
    def extract_relationships(cls, data: Any) -> Any:
        """Extract name fields from relationship objects."""
        if isinstance(data, dict):
            return data

        # Handle SQLAlchemy model objects
        result = {}
        for field_name in cls.model_fields.keys():
            if hasattr(data, field_name):
                value = getattr(data, field_name)
                # Handle relationship objects that have a 'name' attribute
                if hasattr(value, "name"):
                    result[field_name] = value.name
                else:
                    result[field_name] = value
        return result


class Location(LocationBase):
    plant: PlantBase


class LocationSearch(BaseModel):
    id: Optional[int] = None
    code_l1: Optional[int] = None
    continent: Optional[str] = None
    code_l2: Optional[int] = None
    region: Optional[str] = None
    code_l3: Optional[str] = None
    area: Optional[str] = None
    introduced: Optional[bool] = None
    extinct: Optional[bool] = None
    location_doubtful: Optional[bool] = None
    wcvp_plant_id: Optional[int] = None


class LocationSearchResults(BaseModel):
    count: int
    offset: int
    limit: int
    results: list[Location]


class Continent(BaseModel):
    """Continent model."""

    model_config = ConfigDict(from_attributes=True)

    name: str
    code_l1: int


class Region(BaseModel):
    """Region model."""

    model_config = ConfigDict(from_attributes=True)

    name: str
    code_l2: int


class Area(BaseModel):
    """Area model."""

    model_config = ConfigDict(from_attributes=True)

    name: str
    code_l3: str


class PlantLocation(BaseModel):
    """Combined plant and location model."""

    model_config = ConfigDict(from_attributes=True)

    plant_name_id: int
    ipni_id: Optional[str] = None
    family: Optional[str] = None
    taxon_name: str
    taxon_rank: Optional[str] = None
    infraspecific_rank: Optional[str] = None
    infraspecies: Optional[str] = None
    powo_id: Optional[str] = None
    continent: Optional[str] = None
    region: Optional[str] = None
    area: Optional[str] = None
    code_l3: Optional[str] = None


class PlantLocationSearchResults(BaseModel):
    count: int
    offset: int
    limit: int
    results: list[PlantLocation]


class CountryLocation(BaseModel):
    """Country location statistics model."""

    model_config = ConfigDict(from_attributes=True)

    code_l3: str
    species_count: int
