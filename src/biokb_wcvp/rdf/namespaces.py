from rdflib.namespace import Namespace

IPNI_NS = Namespace("https://www.ipni.org/n/")
POWO_NS = Namespace("https://powo.science.kew.org/taxon/")
WCVP_NS = Namespace("https://biokb.scai.fraunhoferde.org/wcvp/id/")
BASE_URI = "https://biokb.scai.fraunhofer.de/wcvp/"
NCBI_TAXON_NS = Namespace("http://purl.obolibrary.org/obo/NCBITaxon_")
NODE_NS = Namespace(f"{BASE_URI}/node#")
REL_NS = Namespace(f"{BASE_URI}/relation#")

# check http://www.tdwg.org/standards/109/ for more details
WGSRPD_BASE = "http://www.tdwg.org/standards/109/"

CONTINENT_NS = Namespace(f"{WGSRPD_BASE}level1/")  # continents of level 1
REGION_NS = Namespace(f"{WGSRPD_BASE}level2/")  # regions of level 2
AREA_NS = Namespace(f"{WGSRPD_BASE}level3/")  # areas of level 3
