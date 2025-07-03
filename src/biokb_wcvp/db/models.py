"""WCVP Database Models"""

from typing import Optional

from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    pass


class Plant(Base):
    __tablename__ = "wcvp_plant"

    id: Mapped[int] = mapped_column(
        primary_key=True, comment="World Checklist of Vascular Plants (WCVP) identifier"
    )
    ipni_id: Mapped[Optional[str]] = mapped_column(
        String(255),
        comment="International Plant Name Index (IPNI) identifier. Missing values indicate that the name has not been matched with a name in IPNI or is missing from IPNI.",
    )
    taxon_rank: Mapped[Optional[str]] = mapped_column(
        String(255),
        comment="The level in the taxonomic hierarchy where the taxon name fits. Some infraspecific names are unranked and will have no value in this column.",
    )
    taxon_status: Mapped[str] = mapped_column(
        String(255),
        comment="Indication of nomenclatural status and taxonomic opinion re the name.",
    )
    family: Mapped[str] = mapped_column(
        String(255),
        comment="The name of the family to which the taxon belongs. (The highest rank at which names are presented in WCVP).",
    )
    genus_hybrid: Mapped[Optional[str]] = mapped_column(
        String(255),
        comment="Indication of hybrid status at genus level: + indicates a graft-chimaera and × indicates a hybrid.",
    )
    genus: Mapped[str] = mapped_column(
        String(255), comment="The name of the genus to which the record refers."
    )
    species_hybrid: Mapped[Optional[str]] = mapped_column(
        String(255),
        comment="Indication of hybrid status at species level: + indicates a graft-chimaera and × indicates a hybrid.",
    )
    species: Mapped[Optional[str]] = mapped_column(
        String(255),
        comment="The species epithet which is combined with the genus name to make a binomial name for a species. Empty when the taxon name is at the rank of genus.",
    )
    infraspecific_rank: Mapped[Optional[str]] = mapped_column(
        String(255),
        comment="The taxonomic rank of the infraspecific epithet. Empty where the taxon name is species rank or higher.",
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
    lifeform_description: Mapped[Optional[str]] = mapped_column(
        String(255),
        comment="The lifeform (or lifeforms) of the taxon. Terms refer to a modified version of the Raunkiær system. Missing values if unknown.",
    )
    climate_description: Mapped[Optional[str]] = mapped_column(
        String(255),
        comment="Habitat type of the taxon, derived from published habitat information.",
    )
    taxon_name: Mapped[str] = mapped_column(
        String(255),
        comment="Concatenation of genus with species and, where applicable, infraspecific epithets to make a binomial or trinomial name.",
    )
    taxon_authors: Mapped[Optional[str]] = mapped_column(
        String(255),
        comment="Concatenation of parenthetical and primary authors. Missing values indicate instances where authorship is unknown or non-applicable (e.g. autonyms).",
    )
    accepted_plant_name_id: Mapped[Optional[int]] = mapped_column(
        comment="The ID of the accepted name of this taxon. Where the taxon_status is 'Accepted', this will be identical to the plant_name_id value."
    )
    basionym_plant_name_id: Mapped[Optional[int]] = mapped_column(
        comment="ID of the original name that taxon_name was derived from. If there is a parenthetical author it is a basionym. If there is a replaced synonym author it is a replaced synonym. If empty there have been no name changes."
    )
    replaced_synonym_author: Mapped[Optional[str]] = mapped_column(
        String(255),
        comment="The author or authors responsible for publication of the replaced synonym. Empty when the name is not a replacement name based on another name.",
    )
    homotypic_synonym: Mapped[Optional[str]] = mapped_column(
        String(255),
        comment="The synonym type - TRUE if homotypic synonym, otherwise NA.",
    )
    parent_plant_name_id: Mapped[Optional[int]] = mapped_column(
        comment="ID for the parent genus or parent species of an accepted species or infraspecific name. Empty for non accepted names or where the parent has not yet been calculated."
    )
    powo_id: Mapped[str] = mapped_column(
        String(255),
        comment="Identifier required to look up the name directly in Plants of the World Online (Powo)",
    )
    hybrid_formula: Mapped[Optional[str]] = mapped_column(
        String(255), comment="Parents of hybrid"
    )
    reviewed: Mapped[Optional[bool]] = mapped_column(
        comment="Flag indicating whether the family to which the taxon belongs has been peer reviewed."
    )

    # relationships
    locations: Mapped[list["Location"]] = relationship(
        back_populates="plant",
    )


class Location(Base):
    __tablename__ = "wcvp_location"

    id: Mapped[int] = mapped_column(primary_key=True)
    continent_code_l1: Mapped[int] = mapped_column(
        comment="Botanical continent code (TDWG Level 1)"
    )
    continent: Mapped[str] = mapped_column(
        String(255), comment="Botanical continent (TDWG Level 1)"
    )
    region_code_l2: Mapped[Optional[int]] = mapped_column(
        comment="Botanical region code (TDWG Level 2)"
    )
    region: Mapped[Optional[str]] = mapped_column(
        String(255), comment="Botanical region (TDWG Level 2)"
    )
    area_code_l3: Mapped[Optional[str]] = mapped_column(
        String(255), comment="Three letter botanical area code (TDWG Level 3)"
    )
    area: Mapped[Optional[str]] = mapped_column(
        String(255), comment="Botanical area (TDWG Level 3)"
    )
    introduced: Mapped[bool] = mapped_column(comment="Introduced status of the taxon")
    extinct: Mapped[bool] = mapped_column(
        comment="Local extinction status of the taxon"
    )
    location_doubtful: Mapped[bool] = mapped_column(comment="Doubtful status of taxon")

    # foreign keys
    wcvp_plant_id: Mapped[int] = mapped_column(
        ForeignKey("wcvp_plant.id"),
        comment="WCVP identifier",
    )

    # relationships
    plant: Mapped["Plant"] = relationship(
        back_populates="locations",
    )
