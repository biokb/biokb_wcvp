"""WCVP Database Models"""

import enum
from typing import Optional

from sqlalchemy import Enum as SAEnum
from sqlalchemy import ForeignKey, Index, String, Text
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship

from biokb_wcvp.constants import PROJECT_NAME
from biokb_wcvp.rdf.namespaces import AREA_NS

table_prefix = PROJECT_NAME + "_"


# TODO: add validate_strings=True to SAEnum when dropping support for SQLite
class Hybrid(enum.Enum):
    GRAFT_CHIMAERA = "+"
    HYBRID = "×"

    @classmethod
    def get_enum(cls):
        return [member.value for member in cls]


class Base(DeclarativeBase):
    pass


class Tree(Base):
    __tablename__ = table_prefix + "tree"

    tree_id: Mapped[int] = mapped_column(primary_key=True)
    tree_parent_id: Mapped[Optional[int]] = mapped_column()
    level: Mapped[int] = mapped_column()
    right_tree_id: Mapped[Optional[int]] = mapped_column()
    is_leaf: Mapped[Optional[bool]] = mapped_column()

    # foreign keys
    plant_name_id: Mapped[int] = mapped_column(
        ForeignKey(table_prefix + "plant.plant_name_id"),
        comment="WCVP Plant name identifier",
    )

    # relationships
    plant: Mapped["Plant"] = relationship(back_populates="tree")


class TaxonRank(Base):
    __tablename__ = table_prefix + "taxon_rank"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(
        String(255), comment="Taxonomic rank of the taxon"
    )

    plants: Mapped[list["Plant"]] = relationship(back_populates="taxon_rank")


class TaxonStatus(Base):
    __tablename__ = table_prefix + "taxon_status"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(
        String(255), comment="Nomenclatural status of the taxon"
    )

    plants: Mapped[list["Plant"]] = relationship(back_populates="taxon_status")


class Family(Base):
    __tablename__ = table_prefix + "family"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(255), comment="Family name of the taxon")

    plants: Mapped[list["Plant"]] = relationship(back_populates="family")


class Genus(Base):
    __tablename__ = table_prefix + "genus"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(255), comment="Genus name of the taxon")

    plants: Mapped[list["Plant"]] = relationship(back_populates="genus")


class InfraspecificRank(Base):
    __tablename__ = table_prefix + "infraspecific_rank"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(
        String(255), comment="Infraspecific rank of the taxon"
    )

    plants: Mapped[list["Plant"]] = relationship(back_populates="infraspecific_rank")


class LifeformDescription(Base):
    __tablename__ = table_prefix + "lifeform_description"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(
        String(255), comment="Lifeform description of the taxon"
    )

    plants: Mapped[list["Plant"]] = relationship(back_populates="lifeform_description")


class ClimateDescription(Base):
    __tablename__ = table_prefix + "climate_description"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(
        String(255),
        comment="Habitat type of the taxon, derived from published habitat information.",
    )

    plants: Mapped[list["Plant"]] = relationship(back_populates="climate_description")


# plant_name_id|ipni_id|taxon_rank|taxon_status|family|genus_hybrid|genus|species_hybrid|species|infraspecific_rank|infraspecies|parenthetical_author|primary_author|publication_author|place_of_publication|volume_and_page|first_published|nomenclatural_remarks|geographic_area|lifeform_description|climate_description|taxon_name|taxon_authors|accepted_plant_name_id|basionym_plant_name_id|replaced_synonym_author|homotypic_synonym|parent_plant_name_id|powo_id|hybrid_formula|reviewed
class Plant(Base):
    __tablename__ = table_prefix + "plant"

    plant_name_id: Mapped[int] = mapped_column(
        primary_key=True, comment="World Checklist of Vascular Plants (WCVP) identifier"
    )
    parent_plant_name_id: Mapped[Optional[int]] = mapped_column(
        comment="ID for the parent genus or parent species of an accepted species or infraspecific name. Empty for non accepted names or where the parent has not yet been calculated.",
    )
    ipni_id: Mapped[Optional[str]] = mapped_column(
        String(255),
        comment="International Plant Name Index (IPNI) identifier. Missing values indicate that the name has not been matched with a name in IPNI or is missing from IPNI.",
    )
    species: Mapped[Optional[str]] = mapped_column(
        String(255),
        comment="The species epithet which is combined with the genus name to make a binomial name for a species. Empty when the taxon name is at the rank of genus.",
    )
    genus_hybrid: Mapped[Optional[str]] = mapped_column(
        String(255),
        comment="Indicates whether the genus is a hybrid (×) or graft-chimaera (+). Empty when the genus is not a hybrid or graft-chimaera.",
    )
    species_hybrid: Mapped[Optional[str]] = mapped_column(
        String(255),
        comment="Indicates whether the species is a hybrid (×) or graft-chimaera (+). Empty when the species is not a hybrid or graft-chimaera.",
    )
    infraspecies: Mapped[Optional[str]] = mapped_column(
        String(255),
        comment="The infraspecific epithet which is combined with a binomial to make a trinomial name at infraspecific rank. Empty when taxon name is at species rank or higher.",
    )
    parenthetical_author: Mapped[Optional[str]] = mapped_column(
        String(255),
        comment="The author of the basionym. Empty when there is no basionym.",
    )
    primary_author: Mapped[Optional[str]] = mapped_column(
        String(255),
        comment="The author or authors who published the scientific name. Missing values indicate instances where authorship is non-applicable (i.e. autonyms) or unknown.",
    )
    publication_author: Mapped[Optional[str]] = mapped_column(
        String(255),
        comment="The author or authors of the book where the scientific name is first published when different from the primary author.",
    )
    place_of_publication: Mapped[Optional[str]] = mapped_column(
        String(255),
        comment="The journal, book or other publication in which the taxon name was effectively published.",
    )
    volume_and_page: Mapped[Optional[str]] = mapped_column(
        String(255),
        comment="The volume and page numbers of the original publication of the taxon name, where '5(6): 36' is volume 5, issue 6, page 36.",
    )
    first_published: Mapped[Optional[str]] = mapped_column(
        String(255),
        comment="The year of publication of the name, enclosed in parentheses. Missing values indicate instances where publication details are unknown or non-applicable (i.e. autonyms).",
    )
    nomenclatural_remarks: Mapped[Optional[str]] = mapped_column(
        String(255),
        comment="Remarks on the nomenclature. Preceded by a comma and space (', ') for easy concatenation.",
    )
    geographic_area: Mapped[Optional[str]] = mapped_column(
        String(255),
        comment="The geographic distribution of the taxon (for names of species rank or below): a generalised statement in narrative form.",
    )
    taxon_name: Mapped[str] = mapped_column(
        String(255),
        index=True,
        comment="Concatenation of genus with species and, where applicable, infraspecific epithets to make a binomial or trinomial name.",
    )
    taxon_authors: Mapped[Optional[str]] = mapped_column(
        String(255),
        comment="Concatenation of parenthetical and primary authors. Missing values indicate instances where authorship is unknown or non-applicable (e.g. autonyms).",
    )
    accepted_plant_name_id: Mapped[Optional[int]] = mapped_column(
        index=True,
        comment="The ID of the accepted name of this taxon. Where the taxon_status is 'Accepted', this will be identical to the plant_name_id value.",
    )
    basionym_plant_name_id: Mapped[Optional[int]] = mapped_column(
        comment="ID of the original name that taxon_name was derived from. If there is a parenthetical author it is a basionym. If there is a replaced synonym author it is a replaced synonym. If empty there have been no name changes."
    )
    replaced_synonym_author: Mapped[Optional[str]] = mapped_column(
        String(255),
        comment="The author or authors responsible for publication of the replaced synonym. Empty when the name is not a replacement name based on another name.",
    )
    homotypic_synonym: Mapped[Optional[bool]] = mapped_column(
        comment="The synonym type - TRUE if homotypic synonym, otherwise NA.",
    )
    powo_id: Mapped[Optional[str]] = mapped_column(
        String(255),
        comment="Identifier required to look up the name directly in Plants of the World Online (Powo). It is only optional for root if not exists before.",
    )
    hybrid_formula: Mapped[Optional[str]] = mapped_column(
        String(255), comment="Parents of hybrid"
    )
    reviewed: Mapped[Optional[bool]] = mapped_column(
        comment="Flag indicating whether the family to which the taxon belongs has been peer reviewed."
    )
    tax_id: Mapped[Optional[int]] = mapped_column(
        index=True,
        comment="NCBI Taxonomy identifier. Missing values indicate that the name has not been matched with a name in NCBI Taxonomy. If possible the tax_id is taken from the accepted name.",
    )
    # foreign keys
    # ================================================================================================================================
    taxon_rank_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey(table_prefix + "taxon_rank.id"),
    )
    taxon_status_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey(table_prefix + "taxon_status.id"),
    )
    family_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey(table_prefix + "family.id"),
    )
    genus_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey(table_prefix + "genus.id"),
    )
    infraspecific_rank_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey(table_prefix + "infraspecific_rank.id"),
    )
    lifeform_description_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey(table_prefix + "lifeform_description.id"),
    )
    climate_description_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey(table_prefix + "climate_description.id"),
    )

    # relationships
    # ================================================================================================================================
    locations: Mapped[list["Location"]] = relationship(
        back_populates="plant",
    )
    taxon_rank: Mapped[Optional["TaxonRank"]] = relationship(back_populates="plants")
    taxon_status: Mapped[Optional["TaxonStatus"]] = relationship(
        back_populates="plants"
    )
    family: Mapped[Optional["Family"]] = relationship(back_populates="plants")
    genus: Mapped[Optional["Genus"]] = relationship(back_populates="plants")
    infraspecific_rank: Mapped[Optional["InfraspecificRank"]] = relationship(
        back_populates="plants"
    )
    lifeform_description: Mapped[Optional["LifeformDescription"]] = relationship(
        back_populates="plants"
    )
    climate_description: Mapped[Optional["ClimateDescription"]] = relationship(
        back_populates="plants"
    )
    tree: Mapped[Optional["Tree"]] = relationship(back_populates="plant")

    def __repr__(self) -> str:
        return f"<Plant: id={self.plant_name_id}, name={self.taxon_name}>"


class TempWcvpPlant(Base):
    """This table is a temporary table for WCVP plants used during data processing."""

    __tablename__ = table_prefix + "temp_plant"
    __table_args__ = {"prefixes": ["TEMPORARY"]}

    plant_name_id: Mapped[int] = mapped_column(
        primary_key=True, comment="World Checklist of Vascular Plants (WCVP) identifier"
    )
    tax_id: Mapped[Optional[int]] = mapped_column(
        index=True,
        comment="NCBI Taxonomy identifier. Missing values indicate that the name has not been matched with a name in NCBI Taxonomy. If possible the tax_id is taken from the accepted name.",
    )


class Continent(Base):
    __tablename__ = table_prefix + "continent"

    code_l1: Mapped[int] = mapped_column(
        primary_key=True, comment="Botanical continent code (TDWG Level 1)"
    )
    name: Mapped[str] = mapped_column(
        String(255), comment="Botanical continent (TDWG Level 1)"
    )

    locations: Mapped[list["Location"]] = relationship(
        back_populates="continent",
    )


class Region(Base):
    __tablename__ = table_prefix + "region"

    code_l2: Mapped[int] = mapped_column(
        primary_key=True, comment="Botanical region code (TDWG Level 2)"
    )
    name: Mapped[str] = mapped_column(
        String(255), comment="Botanical region (TDWG Level 2)"
    )

    locations: Mapped[list["Location"]] = relationship(
        back_populates="region",
    )


class Area(Base):
    __tablename__ = table_prefix + "area"

    code_l3: Mapped[str] = mapped_column(
        String(3),
        primary_key=True,
        comment="Three letter botanical area code (TDWG Level 3)",
    )
    name: Mapped[str] = mapped_column(
        String(255), comment="Botanical area (TDWG Level 3)"
    )
    locations: Mapped[list["Location"]] = relationship(
        back_populates="area",
    )


class Location(Base):
    __tablename__ = table_prefix + "location"

    id: Mapped[int] = mapped_column(primary_key=True)
    introduced: Mapped[bool] = mapped_column(comment="Introduced status of the taxon")
    extinct: Mapped[bool] = mapped_column(
        comment="Local extinction status of the taxon"
    )
    location_doubtful: Mapped[bool] = mapped_column(comment="Doubtful status of taxon")

    # foreign keys
    wcvp_plant_id: Mapped[int] = mapped_column(
        ForeignKey("wcvp_plant.plant_name_id"),
        comment="WCVP identifier",
    )
    code_l1: Mapped[Optional[int]] = mapped_column(
        ForeignKey(table_prefix + "continent.code_l1"),
        comment="continental geographical location level 1 code",
    )
    code_l2: Mapped[Optional[int]] = mapped_column(
        ForeignKey(table_prefix + "region.code_l2"),
        comment="regional geographical location level 2 code",
    )
    code_l3: Mapped[Optional[str]] = mapped_column(
        String(3),
        ForeignKey(table_prefix + "area.code_l3"),
        comment="area geographical location level 3 code",
    )

    # relationships
    plant: Mapped["Plant"] = relationship(
        back_populates="locations",
    )
    continent: Mapped[Optional["Continent"]] = relationship(
        back_populates="locations",
    )
    region: Mapped[Optional["Region"]] = relationship(
        back_populates="locations",
    )
    area: Mapped[Optional["Area"]] = relationship(
        back_populates="locations",
    )


class TaxonomyNameTypes(enum.Enum):
    ACRONYM = "acronym"
    AUTHORITY = "authority"
    BLAST_NAME = "blast name"
    COMMON_NAME = "common name"
    EQUIVALENT_NAME = "equivalent name"
    GENBANK_ACRONYM = "genbank acronym"
    GENBANK_COMMON_NAME = "genbank common name"
    IN_PART = "in-part"
    INCLUDES = "includes"
    SCIENTIFIC_NAME = "scientific name"
    SYNONYM = "synonym"
    TYPE_MATERIAL = "type material"


class TaxonomyName(Base):
    """Class definition for table taxonomy_name. Name from
    NCBI taxonomy https://www.ncbi.nlm.nih.gov/taxonomys."""

    __tablename__ = table_prefix + "taxonomy_name"
    __table_args__ = {"comment": "Taxonomy names by NCBI"}
    id: Mapped[int] = mapped_column(primary_key=True)
    tax_id: Mapped[int] = mapped_column(index=True, comment="NCBI taxonomy Identifier")
    name: Mapped[str] = mapped_column(Text)
    name_type: Mapped[str] = mapped_column(String(255), index=True)
    # name_type: Mapped[str] = mapped_column(
    #     Enum(
    #         TaxonomyNameTypes,
    #         native_enum=True,  # → use real ENUM for MySQL/Postgres
    #         create_constraint=True,  # → fallback CHECK for SQLite/others
    #         validate_strings=True,  # → validates user input
    #     ),
    # )

    __table_args__ = (
        Index(
            "ix_taxonomy_name__name",
            name,
            mysql_length=255,
        ),
    )


# Following location are from Biodiversity Information Standards (TDWG)


class GeoLocationLevel1(Base):
    __tablename__ = table_prefix + "geo_location_level_1"

    code: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(
        String(255), comment="Continental geographical location level 1 name"
    )

    # relationships

    regions: Mapped[list["GeoLocationLevel2"]] = relationship(
        back_populates="continent",
    )

    def __repr__(self) -> str:
        return f"<GeoLocationLevel1: code={self.code}, name={self.name}>"


class GeoLocationLevel2(Base):
    __tablename__ = table_prefix + "geo_location_level_2"

    code: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(
        String(255), comment="Regional geographical location level 2 name"
    )
    level_1_code: Mapped[Optional[int]] = mapped_column(
        ForeignKey(table_prefix + "geo_location_level_1.code"),
    )

    continent: Mapped[Optional["GeoLocationLevel1"]] = relationship(
        back_populates="regions",
    )

    # relationships

    areas: Mapped[list["GeoLocationLevel3"]] = relationship(
        back_populates="region",
    )

    def __repr__(self) -> str:
        return f"<GeoLocationLevel2: code={self.code}, name={self.name}>"


class GeoLocationLevel3(Base):
    __tablename__ = table_prefix + "geo_location_level_3"

    code: Mapped[str] = mapped_column(
        String(3),
        primary_key=True,
    )
    name: Mapped[str] = mapped_column(
        String(255), comment="Area geographical location level 3 name"
    )
    level_2_code: Mapped[Optional[str]] = mapped_column(
        ForeignKey(table_prefix + "geo_location_level_2.code"),
    )

    # relationships

    region: Mapped[Optional["GeoLocationLevel2"]] = relationship(
        back_populates="areas",
    )

    def __repr__(self) -> str:
        return f"<GeoLocationLevel3: code={self.code}, name={self.name}>"
