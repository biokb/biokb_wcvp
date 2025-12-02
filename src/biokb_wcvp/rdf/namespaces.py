from ast import Name

from rdflib.namespace import Namespace

IPNI = Namespace("https://www.ipni.org/id#")
POWO = Namespace("https://powo.science.kew.org/id#")
WCVP = Namespace("https://biokb.scai.fraunhoferde.org/wcvp/id/")
BASE_URI = "https://biokb.scai.fraunhofer.de/wcvp/"
NCBI_TAXON = Namespace("http://purl.obolibrary.org/obo/NCBITaxon_")
node = Namespace(f"{BASE_URI}/node#")
relation = Namespace(f"{BASE_URI}/relation#")

WGSRPD_BASE = "http://rs.tdwg.org/wgsrpd/"

CONTINENT_NS = Namespace(f"{WGSRPD_BASE}level1/")  # continents of level 1
REGION_NS = Namespace(f"{WGSRPD_BASE}level2/")  # regions of level 2
AREA_NS = Namespace(f"{WGSRPD_BASE}level3/")  # areas of level 3
