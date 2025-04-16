from sqlalchemy import Boolean, Date, ForeignKey, Integer, String
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship

from wcvp.constants import PROJECT_NAME


class Base(DeclarativeBase):
    _prefix = PROJECT_NAME + "_"


class Family(Base):
    __tablename__ = Base._prefix + "family"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(255), unique=True)

    genera: Mapped[list["Genus"]] = relationship(
        "Genus", back_populates="family", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<Family: name={self.name}>"


class Genus(Base):
    __tablename__ = Base._prefix + "genus"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(255), unique=True)
    family_id: Mapped[int] = mapped_column(ForeignKey(Base._prefix + "family.id"))

    family: Mapped["Family"] = relationship("Family", back_populates="genera")
    species: Mapped[list["Species"]] = relationship("Species", back_populates="genus")


class Species(Base):
    __tablename__ = Base._prefix + "species"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(255), unique=True)

    genus_id: Mapped[int] = mapped_column(ForeignKey(Base._prefix + "genus.id"))
    genus: Mapped["Genus"] = relationship("Genus", back_populates="species")


class TaxonRank(Base):
    __tablename__ = Base._prefix + "taxon_rank"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    rank: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)

    taxons: Mapped[list["Taxon"]] = relationship("Taxon", back_populates="rank")

    def __repr__(self) -> str:
        return f"<TaxonRank: rank={self.rank}>"


class TaxonStatus(Base):
    __tablename__ = Base._prefix + "taxon_status"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    status: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)

    taxons: Mapped[list["Taxon"]] = relationship("Taxon", back_populates="status")

    def __repr__(self) -> str:
        return f"<TaxonStatus: name={self.status}>"


class Taxon(Base):
    __tablename__ = Base._prefix + "taxon"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    taxon_name: Mapped[str] = mapped_column(String(255), nullable=False, unique=True)

    rank_id: Mapped[int] = mapped_column(
        Integer, ForeignKey(Base._prefix + "taxon_rank.id"), nullable=False
    )
    status_id: Mapped[int] = mapped_column(
        Integer, ForeignKey(Base._prefix + "taxon_status.id"), nullable=False
    )

    rank: Mapped["TaxonRank"] = relationship("TaxonRank", back_populates="taxons")
    status: Mapped["TaxonStatus"] = relationship("TaxonStatus", back_populates="taxons")

    plants: Mapped[list["Plant"]] = relationship("Plant", back_populates="taxon")

    def __repr__(self) -> str:
        return f"<Taxon: name={self.taxon_name}>"


class InfraSpecies(Base):
    __tablename__ = Base._prefix + "infraspecies"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(255), unique=True)

    plants: Mapped[list["Plant"]] = relationship("Plant", back_populates="infraspecies")


class LifeFormDescription(Base):
    __tablename__ = Base._prefix + "lifeform_description"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    description: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)

    environmental_descriptions: Mapped[list["EnvironmentalDescription"]] = relationship(
        "EnvironmentalDescription", back_populates="lifeform"
    )

    def __repr__(self) -> str:
        return f"<LifeformDescription: description={self.description}>"


class ClimateDescription(Base):
    __tablename__ = Base._prefix + "climate_description"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    description: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)

    environmental_descriptions: Mapped[list["EnvironmentalDescription"]] = relationship(
        "EnvironmentalDescription", back_populates="climate"
    )

    def __repr__(self) -> str:
        return f"<ClimateDescription: description={self.description}>"


class EnvironmentalDescription(Base):
    __tablename__ = Base._prefix + "environmental_description"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    lifeform_id: Mapped[int] = mapped_column(
        ForeignKey(Base._prefix + "lifeform_description.id"), nullable=True
    )
    climate_id: Mapped[int] = mapped_column(
        ForeignKey(Base._prefix + "climate_description.id"), nullable=False
    )

    lifeform: Mapped["LifeFormDescription"] = relationship(
        "LifeformDescription", back_populates="environmental_descriptions"
    )
    climate: Mapped["ClimateDescription"] = relationship(
        "ClimateDescription", back_populates="environmental_descriptions"
    )
    plants: Mapped[list["Plant"]] = relationship(
        "Plant", back_populates="environmental_description"
    )

    def __repr__(self) -> str:
        return f"<EnvironmentalDescription: name={self.id}>"


class Continent(Base):
    __tablename__ = Base._prefix + "continent"
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    code: Mapped[int] = mapped_column(unique=True)  # continent_code_l1
    name: Mapped[str] = mapped_column(String(255), unique=True)  # continent

    geographic_area: Mapped[list["GeographicArea"]] = relationship(
        back_populates="continent", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<Continent: name={self.name}, code={self.code}>"


class Region(Base):
    __tablename__ = Base._prefix + "region"
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    code: Mapped[float] = mapped_column(unique=True)  # region_code_l2
    name: Mapped[str] = mapped_column(String(255), unique=True)  # region

    geographic_area: Mapped[list["GeographicArea"]] = relationship(
        back_populates="region", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<Region: name={self.name}, code={self.code}>"


class Area(Base):
    __tablename__ = Base._prefix + "area"
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    code: Mapped[str] = mapped_column(
        String(255), unique=True, nullable=True
    )  # area_code_l3
    name: Mapped[str] = mapped_column(String(255), unique=True, nullable=True)  # area

    geographic_area: Mapped[list["GeographicArea"]] = relationship(
        back_populates="area", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<Area: name={self.name}, code={self.code}>"


class GeographicArea(Base):
    __tablename__ = Base._prefix + "geographic_area"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(255), unique=True, nullable=True)

    area_id: Mapped[int] = mapped_column(ForeignKey(Base._prefix + "area.id"))
    region_id: Mapped[int] = mapped_column(ForeignKey(Base._prefix + "region.id"))
    continent_id: Mapped[int] = mapped_column(ForeignKey(Base._prefix + "continent.id"))

    plants: Mapped[list["Plant"]] = relationship(
        back_populates="geographic_area", cascade="all, delete-orphan"
    )
    area: Mapped[Area] = relationship(back_populates="geographic_area")
    region: Mapped[Region] = relationship(back_populates="geographic_area")
    continent: Mapped[Continent] = relationship(back_populates="geographic_area")

    def __repr__(self) -> str:
        return f"<GeographicArea: name={self.id}>"


class Publication(Base):
    __tablename__ = Base._prefix + "publication"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    primary_author: Mapped[str] = mapped_column(String(255))
    first_published: Mapped[Date] = mapped_column(Date)

    plants: Mapped[list["Plant"]] = relationship("Plant", back_populates="publication")

    def __repr__(self) -> str:
        return (
            f"<Publication: author={self.primary_author}, title={self.first_published}>"
        )


class Plant(Base):
    __tablename__ = "plant"

    plant_name_id: Mapped[int] = mapped_column(Integer, primary_key=True)
    ipni_id: Mapped[str] = mapped_column(String(255), unique=True)
    reviewed: Mapped[bool] = mapped_column(Boolean, default=False)
    introduced: Mapped[bool] = mapped_column(Boolean, default=False)
    extinct: Mapped[bool] = mapped_column(Boolean, default=False)
    location_doubtful: Mapped[bool] = mapped_column(Boolean, default=False)

    # Foreign keys for relationships
    family_id: Mapped[int] = mapped_column(ForeignKey(Base._prefix + "family.id"))
    genus_id: Mapped[int] = mapped_column(ForeignKey(Base._prefix + "genus.id"))
    species_id: Mapped[int] = mapped_column(ForeignKey(Base._prefix + "species.id"))
    infraspecies_id: Mapped[int] = mapped_column(
        ForeignKey(Base._prefix + "infraspecies.id")
    )
    publication_id: Mapped[int] = mapped_column(
        ForeignKey(Base._prefix + "publication.id")
    )
    taxon_id: Mapped[int] = mapped_column(ForeignKey(Base._prefix + "taxon.id"))
    geographic_area_id: Mapped[int] = mapped_column(
        ForeignKey(Base._prefix + "geographic_area.id")
    )
    environmental_description_id: Mapped[int] = mapped_column(
        ForeignKey(Base._prefix + "environmental_description.id"), nullable=True
    )

    # Relationships
    family: Mapped["Family"] = relationship("Family")
    genus: Mapped["Genus"] = relationship("Genus")
    species: Mapped["Species"] = relationship("Species")
    infraspecies: Mapped["InfraSpecies"] = relationship("Infraspecies")
    publication: Mapped["Publication"] = relationship(
        "Publication", back_populates="plants"
    )
    taxon: Mapped["Taxon"] = relationship("Taxon", back_populates="plants")
    geographic_area: Mapped[list["GeographicArea"]] = relationship(
        "GeographicArea", back_populates="plants"
    )
    environmental_description: Mapped["EnvironmentalDescription"] = relationship(
        "EnvironmentalDescription", back_populates="plants"
    )

    def __repr__(self) -> str:
        return f"<Plant: ipni_id={self.ipni_id}>"
