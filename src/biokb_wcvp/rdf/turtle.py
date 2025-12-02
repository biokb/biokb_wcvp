"""Module to create RDF turtle files from the WCVP (World Checklist of Vascular Plants) data.

This module provides functionality to export taxonomic and geographic data from a SQL database
into RDF Turtle format, suitable for semantic web applications and knowledge graphs.
"""

import logging
import os.path
import shutil
from typing import List, Type, TypeVar
from urllib.parse import urlparse

from rdflib import RDF, XSD, Graph, Literal, Namespace, URIRef
from sqlalchemy import Engine
from sqlalchemy.orm import sessionmaker
from tqdm import tqdm

logger = logging.getLogger(__name__)


from biokb_wcvp.constants import (
    BASIC_NODE_LABEL,
    DATA_FOLDER,
    EXPORT_FOLDER,
    TAXONOMY_URL,
)
from biokb_wcvp.db import models
from biokb_wcvp.rdf import namespaces

# Type variable for SQLAlchemy model classes
BaseModels = TypeVar("BaseModels", bound=models.Base)


def get_namespace(model: Type[models.Base]) -> Namespace:
    """Generate an RDF namespace for a given SQLAlchemy model class.

    Args:
        model: SQLAlchemy model class to generate namespace for.

    Returns:
        RDF Namespace object with URI based on the model's class name.
    """
    return Namespace(f"{namespaces.BASE_URI}/{model.__name__}#")


def get_empty_graph() -> Graph:
    """Create an empty RDFlib Graph with all required namespace bindings.

    The graph is pre-configured with namespace prefixes for:
    - node: Generic node types
    - rel: Relationships between entities
    - xs: XML Schema datatypes
    - con/reg/are: TDWG geographic levels (continents, regions, areas)
    - p: Plant taxonomic names
    - po: POWO (Plants of the World Online) identifiers
    - ip: IPNI (International Plant Names Index) identifiers
    - nc: NCBI Taxonomy identifiers

    Returns:
        An RDFlib Graph object with all namespace bindings configured.
    """
    graph = Graph()
    # Bind generic ontology namespaces
    graph.bind(prefix="node", namespace=namespaces.node)
    graph.bind(prefix="rel", namespace=namespaces.relation)
    graph.bind(prefix="xs", namespace=XSD)

    # Bind geographic namespaces (TDWG World Geographical Scheme)
    graph.bind(prefix="con", namespace=namespaces.CONTINENT_NS)
    graph.bind(prefix="reg", namespace=namespaces.REGION_NS)
    graph.bind(prefix="are", namespace=namespaces.AREA_NS)

    # Bind taxonomic and identifier namespaces
    graph.bind(prefix="p", namespace=get_namespace(models.Plant))
    graph.bind(prefix="po", namespace=namespaces.POWO)
    graph.bind(prefix="ip", namespace=namespaces.IPNI)
    graph.bind(prefix="nc", namespace=namespaces.NCBI_TAXON)

    return graph


class TurtleCreator:
    """Factory class for generating RDF Turtle files from WCVP database.

    This class handles the export of plant taxonomic data and geographic distributions
    from a relational database into RDF Turtle format for use in semantic web applications.
    """

    def __init__(
        self,
        engine: Engine | None = None,
        export_to_folder: str | None = None,
        data_folder: str | None = None,
    ):
        """Initialize the TurtleCreator with database and file system settings.

        Args:
            engine: SQLAlchemy database engine. Uses default if None.
            export_to_folder: Directory for exporting turtle files. Uses EXPORT_FOLDER constant if None.
            data_folder: Directory containing source data files. Uses DATA_FOLDER constant if None.

        Raises:
            FileExistsError: If the specified data_folder does not exist.
            Exception: If the taxonomy file is not found in the data_folder.
        """
        # Set up the export folder for turtle files
        if export_to_folder:
            ttls_folder = os.path.join(export_to_folder, "ttls")
            self.__ttls_folder = ttls_folder
        else:
            self.__ttls_folder = EXPORT_FOLDER

        # Create export folder if it doesn't exist
        if not os.path.exists(self.__ttls_folder):
            os.makedirs(self.__ttls_folder)

        # Validate and set up the data folder
        if data_folder:
            if os.path.exists(data_folder):
                taxonomy_file_name = os.path.basename(urlparse(TAXONOMY_URL).path)
                if taxonomy_file_name not in os.listdir(data_folder):
                    raise Exception(
                        f"Taxonomy file '{taxonomy_file_name}' not found in {data_folder}"
                    )
                self.__data_folder = data_folder
            else:
                raise FileExistsError(f"Data folder '{data_folder}' does not exist")
        else:
            self.__data_folder = DATA_FOLDER

        # Set up database engine and session factory
        self.__engine = engine
        self.Session = sessionmaker(bind=self.__engine)

    def create_all_ttls(self) -> str:
        """Create all RDF turtle files and package them into a zip archive.

        This method orchestrates the complete export process:
        1. Creates TDWG geographic location hierarchy
        2. Creates plant taxonomic name entries
        3. Links plants to their geographic distributions
        4. Packages all turtle files into a zip archive

        Returns:
            Path to the created zip file containing all turtle files.
        """
        logging.info("Starting turtle file generation process.")

        # Generate individual turtle files in order
        self.create_tdwg_locations()  # Geographic hierarchy first
        self.create_plants()  # Then taxonomic data
        self.create_locations()  # Finally, distribution links

        # Package everything into a zip file
        path_to_zip_file: str = self.create_zip_from_all_ttls()
        logging.info(f"Turtle files successfully packaged in {path_to_zip_file}")
        return path_to_zip_file

    def create_locations(self):
        """Create RDF triples linking plants to their geographic distributions.

        For each accepted plant name, this creates HAS_LOCATION relationships to TDWG
        geographic units at the most specific level available (Area > Region > Continent).
        """
        logging.info("Creating RDF plant distribution turtle file.")
        graph = get_empty_graph()

        with self.Session() as session:
            # Query only accepted plant names (not synonyms)
            plants: List[models.Plant] = (
                session.query(models.Plant)
                .where(
                    models.Plant.accepted_plant_name_id == models.Plant.plant_name_id
                )
                .all()
            )

            plant_namespace: Namespace = get_namespace(models.Plant)

            for plant in tqdm(plants, desc="Creating plant-location links"):
                p: URIRef = plant_namespace[str(plant.plant_name_id)]

                # Link to the most specific geographic level available for each location
                for location in plant.locations:
                    if location.extinct == True:
                        continue  # Skip extinct locations
                    if location.code_l3:  # Level 3: Botanical area (most specific)
                        graph.add(
                            triple=(
                                p,
                                namespaces.relation["HAS_LOCATION"],
                                namespaces.AREA_NS[str(location.code_l3)],
                            )
                        )

                    elif location.code_l2:  # Level 2: Region
                        graph.add(
                            triple=(
                                p,
                                namespaces.relation["HAS_LOCATION"],
                                namespaces.REGION_NS[str(location.code_l2)],
                            )
                        )
                    elif location.code_l1:  # Level 1: Continent (least specific)
                        graph.add(
                            triple=(
                                p,
                                namespaces.relation["HAS_LOCATION"],
                                namespaces.CONTINENT_NS[str(location.code_l1)],
                            )
                        )

        # Serialize and save the graph
        ttl_path = os.path.join(self.__ttls_folder, "wcvp_locations.ttl")
        graph.serialize(ttl_path, format="turtle")
        del graph

    def create_plants(self):
        """Create RDF nodes for all accepted plant taxonomic names.

        For each plant, this creates:
        - Type declarations (Plant and basic node)
        - External identifier links (IPNI, POWO, NCBI Taxonomy)
        - Taxonomic name as literal
        - Parent taxon relationship for hierarchical navigation
        """
        logging.info("Creating RDF plant taxonomy turtle file.")
        graph = get_empty_graph()

        with self.Session() as session:
            # Query only accepted plant names (excluding synonyms)
            plants: List[models.Plant] = (
                session.query(models.Plant)
                .where(
                    models.Plant.accepted_plant_name_id == models.Plant.plant_name_id
                )
                .all()
            )

            plant_namespace: Namespace = get_namespace(models.Plant)

            for plant in tqdm(plants, desc="Creating plant taxonomy nodes"):
                p: URIRef = plant_namespace[str(plant.plant_name_id)]

                # Add type declarations
                graph.add(
                    triple=(
                        p,
                        RDF.type,
                        namespaces.node[models.Plant.__name__],
                    )
                )
                graph.add(triple=(p, RDF.type, namespaces.node[BASIC_NODE_LABEL]))

                # Link to external plant name databases if available
                if plant.ipni_id:
                    graph.add(
                        triple=(
                            p,
                            namespaces.relation["HAS_IPNI"],
                            namespaces.IPNI[plant.ipni_id],
                        )
                    )
                if plant.powo_id:
                    graph.add(
                        triple=(
                            p,
                            namespaces.relation["HAS_POWO"],
                            namespaces.POWO[plant.powo_id],
                        )
                    )

                # Add the taxonomic name as a literal string
                graph.add(
                    triple=(
                        p,
                        namespaces.relation["taxon_name"],
                        Literal(lexical_or_value=plant.taxon_name, datatype=XSD.string),
                    )
                )

                # Link to parent taxon for hierarchical structure
                if plant.parent_plant_name_id:
                    graph.add(
                        triple=(
                            p,
                            namespaces.relation["HAS_PARENT"],
                            plant_namespace[str(plant.parent_plant_name_id)],
                        )
                    )

                # Link to NCBI Taxonomy if available
                if plant.tax_id:
                    graph.add(
                        triple=(
                            p,
                            namespaces.relation["HAS_NCBI_TAXON"],
                            namespaces.NCBI_TAXON[str(int(plant.tax_id))],
                        )
                    )

        # Serialize and save the graph
        ttl_path = os.path.join(self.__ttls_folder, "wcvp_plants.ttl")
        graph.serialize(ttl_path, format="turtle")
        del graph

    def create_tdwg_locations(self):
        """Create RDF turtle file for TDWG World Geographical Scheme for Recording Plant Distributions.

        Builds a hierarchical geographic ontology with three levels:
        - Level 1: Continents (9 major continental divisions)
        - Level 2: Regions (52 geographic regions)
        - Level 3: Areas (369 basic geographic units)

        Each level includes name literals and hierarchical relationships (HAS_REGION, HAS_AREA).
        """
        logging.info("Creating RDF TDWG geographic hierarchy turtle file.")
        graph = get_empty_graph()

        with self.Session() as session:
            # Retrieve all continents (Level 1) with their nested regions and areas
            continents: List[models.GeoLocationLevel1] = session.query(
                models.GeoLocationLevel1
            ).all()

            for continent in tqdm(
                continents, desc="Creating TDWG Level 1 (Continents) entries"
            ):
                # Create Level 1 (Continent) node
                l1: URIRef = namespaces.CONTINENT_NS[str(continent.code)]
                graph.add(triple=(l1, RDF.type, namespaces.node["Continent"]))
                graph.add(triple=(l1, RDF.type, namespaces.node["DbTdwgLocation"]))
                graph.add(
                    triple=(
                        l1,
                        namespaces.relation["continent"],
                        Literal(continent.name, datatype=XSD.string),
                    )
                )

                # Process Level 2 (Regions) within this continent
                for region in continent.regions:
                    l2: URIRef = namespaces.REGION_NS[str(region.code)]
                    graph.add(triple=(l2, RDF.type, namespaces.node["Region"]))
                    graph.add(triple=(l2, RDF.type, namespaces.node["DbTdwgLocation"]))
                    graph.add(
                        triple=(
                            l2,
                            namespaces.relation["continent"],
                            Literal(continent.name, datatype=XSD.string),
                        )
                    )

                    graph.add(
                        triple=(
                            l2,
                            namespaces.relation["region"],
                            Literal(region.name, datatype=XSD.string),
                        )
                    )

                    # Link region to its parent continent
                    graph.add(
                        triple=(
                            l1,
                            namespaces.relation["HAS_REGION"],
                            l2,
                        )
                    )

                    # Process Level 3 (Areas) within this region
                    for area in region.areas:
                        l3: URIRef = namespaces.AREA_NS[str(area.code)]
                        graph.add(triple=(l3, RDF.type, namespaces.node["Area"]))
                        graph.add(
                            triple=(l3, RDF.type, namespaces.node["DbTdwgLocation"])
                        )
                        graph.add(
                            triple=(
                                l3,
                                namespaces.relation["continent"],
                                Literal(continent.name, datatype=XSD.string),
                            )
                        )

                        graph.add(
                            triple=(
                                l3,
                                namespaces.relation["region"],
                                Literal(region.name, datatype=XSD.string),
                            )
                        )
                        graph.add(
                            triple=(
                                l3,
                                namespaces.relation["area"],
                                Literal(area.name, datatype=XSD.string),
                            )
                        )
                        # Link area to its parent region
                        graph.add(
                            triple=(
                                l2,
                                namespaces.relation["HAS_AREA"],
                                l3,
                            )
                        )

        # Serialize and save the graph
        ttl_path = os.path.join(self.__ttls_folder, "tdwg_locations.ttl")
        graph.serialize(ttl_path, format="turtle")
        del graph

    def create_zip_from_all_ttls(self) -> str:
        """Package all generated turtle files into a single zip archive.

        Creates a zip file containing all .ttl files in the export folder,
        then removes the temporary turtle files directory to clean up.

        Returns:
            Path to the created zip file.
        """
        logger.info("Packaging turtle files into zip archive.")

        # Create zip archive from all turtle files
        path_to_zip_file = shutil.make_archive(
            base_name=self.__ttls_folder, format="zip", root_dir=self.__ttls_folder
        )

        # Clean up temporary turtle files directory
        shutil.rmtree(self.__ttls_folder)

        return path_to_zip_file
