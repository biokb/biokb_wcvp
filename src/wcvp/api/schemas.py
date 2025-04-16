from enum import Enum
from pydantic import BaseModel, Field


class Family(BaseModel):
    id: int
    name: str
class FamilyCreate(BaseModel):
    name: str

class Genus(BaseModel):
    id: int
    name: str
    family_id: int   
class GenusCreate(BaseModel):
    name: str
    family_name: str

class Species(BaseModel):
    id: int
    name: str
    genus_id: int
class SpeciesCreate(BaseModel):
    name: str
    genus_name: str

class Area(BaseModel):
    id: int
    code: str
    name: str
class AreaCreate(BaseModel):
    code: str
    name: str

class Region(BaseModel):
    id: int
    code: int
    name: str
class RegionCreate(BaseModel):
    code: int
    name: str

class Continent(BaseModel):
    id: int
    code: int
    name: str
class ContinentCreate(BaseModel):
    code: int
    name: str

class Geographic_Area(BaseModel):
    id: int
    name: str
    area_id: int
    region_id: int
    continent_id: int
class Geographic_AreaCreate(BaseModel):
    name: str
    area_name: str
    region_name: str
    continent_name: str

class Climate(BaseModel):
    id: int
    description: str
class ClimateCreate(BaseModel):
    description: str

class LifeForm(BaseModel):
    id: int
    description: str
class LifeFormCreate(BaseModel):
    description: str

class Environment(BaseModel):
    id: int
    lifeform_id: int
    climate_id: int
class EnvironmentCreate(BaseModel):
    lifeform_description: str
    climate_description: str

class Taxon(BaseModel):
    id: int
    taxon_name: str
    rank_id: int
    status_id: int
class TaxonCreate(BaseModel):
    taxon_name: str
    taxon_rank: str
    taxon_status: str


class Plant(BaseModel):
    #id: int
    plant_name_id:int
    reviewed: bool
    ipni_id:str
    introduced: bool
    extinct: bool
    location_doubtful: bool

    # foreign keys
    family_id: int
    genus_id: int
    species_id: int
    taxon_id: int

    geographic_area_id: int
    environmental_description_id: int

    publication_id: int
    infraspecies_id: int  
     
class PlantCreate(BaseModel):
    plant_name_id: int
    reviewed: str = Field(
        default="N",
        title="Reviewed",
        json_schema_extra={"enum": ["N", "Y"]}
    )
    ipni_id:str
    introduced: str = Field(
        default="N",
        title="Introduced",
        json_schema_extra={"enum": ["N", "Y"]}
    )
    extinct: str = Field(
        default="N",
        title="Extinct",
        json_schema_extra={"enum": ["N", "Y"]}
    )
    location_doubtful: str = Field(
        default="N",
        title="Location Doubtful",
        json_schema_extra={"enum": ["N", "Y"]}
    )
    # foreign keys
    # class Taxon
    taxon_name: str
    taxon_status: str
    taxon_rank: str

    family_name: str
    genus_name: str
    species_name: str

    # class publication
    primary_author_name: str
    first_published: str
    
    # class Geographic_area
    geographic_area_name: str
    area_code:str
    area_name:str
    region_code:int
    region_name:str
    continent_code:int
    continent_name: str

    # class environment
    lifeform_description: str
    climate_description: str
    
    # infraspecies
    infraspecies_name: str
    

'''
class PlantID(BaseModel):
    id: int
    plant_name_id: int

class PlantIDCreate(BaseModel):
    plant_name_id: int
'''