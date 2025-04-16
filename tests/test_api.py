from fastapi.testclient import TestClient
from wcvp.api.main import app
import os.path
from fastapi import status
import pytest

client = TestClient(app)


def create_fresh_db():
    file_name = "test_data.csv"
    test_file = os.path.join("tests", "data/test_data", file_name)
    file = {"file": (file_name, open(test_file, "rb"))}
    response = client.post("/load_db_from_csv/", files=file)
    return response


def get_openapi_doc_dict():
    return client.get("/openapi.json").json()


def test_hello_world():
    response = client.get("/")
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {"msg": "Hello World"}


class TestOpenApi:
    def test_all_endpoint(self):
        open_api_doc_dict = get_openapi_doc_dict()
        set_api_endpoints = set(open_api_doc_dict["paths"].keys())
        expected_endpoints = {
            "/load_db_from_csv/",
            "/",
            "/families/",
            "/family/create/",
            "/family/{id}",
            "/genus/",
            "/genus/create/",
            "/genus/{id}",
            "/species/",
            "/species/create/",
            "/species/{id}",
            "/areas/",
            "/area/create/",
            "/area/{id}",
            "/regions/",
            "/region/create/",
            "/region/{id}",
            "/continents/",
            "/continent/create/",
            "/continent/{id}",
            "/geographic_areas/",
            "/climates/",
            "/climate/create/",
            "/climate/{id}",
            "/life_forms/",
            "/life_form/create/",
            "/taxon/create/",
            "/taxon/{taxon_name}",
            "/taxons/",
            "/taxons/by_taxon_rank/",
            "/taxons/by_taxon_status/",
            "/plant/create/",
            "/plant/{plant_name_id}",
            "/plants/",
            "/plants/by_family/",
            "/plants/by_genus/",
            "/plants/by_species/",
            "/plants/by_extinction/",
            "/plants/by_climate/",
            "/plants/by_lifeform/",
            "/plants/by_area/",
            "/plants/by_region/",
            "/plants/by_continent/",
        }
        missing_endpoints = expected_endpoints - set_api_endpoints
        extra_endpoints = set_api_endpoints - expected_endpoints

        print("Missing endpoints:", missing_endpoints)
        print("Extra endpoints:", extra_endpoints)

        assert expected_endpoints.issubset(set_api_endpoints)

    @pytest.mark.parametrize(
        "endpoint,method,tag",
        [
            ("/families/", "get", "Family"),
            ("/family/create/", "post", "Family"),
            ("/family/{id}", "get", "Family"),
            ("/load_db_from_csv/", "post", "Database Management"),
            ("/taxon/create/", "post", "Taxon"),
            ("/taxon/{taxon_name}", "delete", "Taxon"),
            ("/taxons/", "get", "Taxon"),
            ("/plants/by_family/", "get", "Plant"),
        ],
    )
    def test_tags(self, endpoint, method, tag):
        open_api_doc_dict = get_openapi_doc_dict()
        assert method in open_api_doc_dict["paths"][endpoint].keys()
        assert open_api_doc_dict["paths"][endpoint][method]["tags"] == [tag]

    def test_schemas_created(self):
        open_api_doc_dict = get_openapi_doc_dict()
        schemas = set(open_api_doc_dict["components"]["schemas"].keys())
        expected_schemas = {
            "Family",
            "FamilyCreate",
            "Taxon",
            "TaxonCreate",
            "Area",
            "AreaCreate",
            "Plant",
            "PlantCreate",
        }
        assert expected_schemas.issubset(schemas)


class TestFamily:

    def test_family_schema(self):
        open_api_doc_dict = get_openapi_doc_dict()
        schemas = open_api_doc_dict["components"]["schemas"]
        assert schemas["Family"]["required"] == [
            "id",
            "name",
        ]

    def test_family_create_schema(self):
        open_api_doc_dict = get_openapi_doc_dict()
        schemas = open_api_doc_dict["components"]["schemas"]
        assert schemas["FamilyCreate"]["required"] == ["name"]

    def test_plant_schema(self):
        open_api_doc_dict = get_openapi_doc_dict()
        schemas = open_api_doc_dict["components"]["schemas"]
        assert schemas["Plant"]["required"] == [
            "plant_name_id",
            "reviewed",
            "ipni_id",
            "introduced",
            "extinct",
            "location_doubtful",
            "family_id",
            "genus_id",
            "species_id",
            "taxon_id",
            "geographic_area_id",
            "environmental_description_id",
            "publication_id",
            "infraspecies_id",
        ]

    def test_plant_create_schema(self):
        open_api_doc_dict = get_openapi_doc_dict()
        # test for PlantCreate schema
        schemas = open_api_doc_dict["components"]["schemas"]
        assert schemas["PlantCreate"]["required"] == [
            "plant_name_id",
            "ipni_id",
            # foreign keys
            "taxon_name",
            "taxon_status",
            "taxon_rank",
            "family_name",
            "genus_name",
            "species_name",
            "primary_author_name",
            "first_published",
            "geographic_area_name",
            "area_code",
            "area_name",
            "region_code",
            "region_name",
            "continent_code",
            "continent_name",
            "lifeform_description",
            "climate_description",
            "infraspecies_name",
        ]
        assert schemas["PlantCreate"]["properties"]["reviewed"] == {
            "type": "string",
            "enum": ["N", "Y"],
            "title": "Reviewed",
            "default": "N",
        }

    def test_load_db_from_csv(self):
        file_name = "test_data.csv"
        test_file = os.path.join("tests", "data/test_data", file_name)
        file = {"file": (file_name, open(test_file, "rb"))}
        response = client.post("/load_db_from_csv/", files=file)
        assert response.status_code == status.HTTP_200_OK
        assert response.json() == {"loaded": True}

    def test_create_family(self):
        create_fresh_db()
        response = client.post("/family/create/", json={"name": "test_family"})
        assert response.json() == {"id": 11, "name": "test_family"}

    def test_get_families_default(self):
        response = client.get("/families/")
        assert len(response.json()) == 3

    def test_get_families(self):
        response = client.get("/families/?offset=1&limit=2")
        assert len(response.json()) == 2

    def test_get_families_limit_too_high(self):
        response = client.get("/families/?offset=1&limit=11")
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
        assert (
            response.json()["detail"][0]["msg"]
            == "Input should be less than or equal to 10"
        )

    def test_get_family_by_id(self):
        response = client.get("/family/1")
        assert response.json() == {"id": 1, "name": "Oxalidaceae"}


class TestTaxon:

    def test_create_taxon(self):
        create_fresh_db()
        data = {
            "taxon_name": "test_name",
            "taxon_rank": "species",
            "taxon_status": "test",
        }
        response = client.post("/taxon/create/", json=data)
        print("left\n", response)
        assert response.json() == {
            "id": 12,
            "taxon_name": "test_name",
            "status_id": 3,
            "rank_id": 2,
        }

    def test_get_taxons_by_taxon_status(self):
        response = client.get("/taxons/by_taxon_status/?taxon_status=Accepted")
        assert len(response.json()) == 10

    def test_get_taxons_default(self):
        response = client.get("/taxons/")
        assert len(response.json()) == 3

    def test_get_taxons(self):
        response = client.get("/taxons/?offset=1&limit=2")
        assert len(response.json()) == 2

    def test_get_taxons_limit_too_high(self):
        response = client.get("/taxons/?offset=1&limit=11")
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
        assert (
            response.json()["detail"][0]["msg"]
            == "Input should be less than or equal to 10"
        )


class TestPlant:

    def test_create_plant(self):
        create_fresh_db()
        data = {
            "plant_name_id": 1,
            "ipni_id": "1-1",
            # foreign keys
            "taxon_name": "test_name",
            "taxon_status": "test_status",
            "taxon_rank": "species",
            "family_name": "test_family",
            "genus_name": "test_genus",
            "species_name": "test_species",
            "primary_author_name": "test_author",
            "first_published": "1995-10-23",
            "geographic_area_name": "blabla",
            "area_code": "area_code",
            "area_name": "aaa",
            "region_code": 123,
            "region_name": "ghj",
            "continent_code": 321,
            "continent_name": "ert",
            "lifeform_description": "fgh",
            "climate_description": "rty",
            "infraspecies_name": "rt",
        }
        response = client.post("/plant/create/", json=data)
        print("left\n", response)
        assert response.json() == {
            "plant_name_id": 1,
            "reviewed": False,
            "ipni_id": "1-1",
            "introduced": False,
            "extinct": False,
            "location_doubtful": False,
            "family_id": 11,
            "genus_id": 11,
            "species_id": 12,
            "taxon_id": 12,
            "publication_id": 12,
            "geographic_area_id": 12,
            "environmental_description_id": 10,
            "infraspecies_id": 4,
        }

    def test_get_plants_by_family(self):
        response = client.get("/plants/by_family/?name=Asteraceae")
        assert len(response.json()) == 1

    def test_get_plants_by_genus(self):
        response = client.get("/plants/by_genus/?name=Picramnia")
        assert len(response.json()) == 1

    def test_get_plants_by_species(self):
        response = client.get("/plants/by_species/?name=dentata")
        assert len(response.json()) == 1

    def test_get_plants_by_extinction(self):
        # Test with extinction=False (0)
        response = client.get("/plants/by_extinction/?extinction=0")
        assert response.status_code == 200
        assert isinstance(response.json(), list)  # Ensure response is a list
        assert len(response.json()) == 11

        # Test with extinction=True (1)
        response = client.get("/plants/by_extinction/?extinction=1")
        assert response.status_code == 200
        assert isinstance(response.json(), list)  # Ensure response is a list
        assert (
            len(response.json()) == 1
        )  # Expected number of results for extinct taxons

    def test_get_plants_by_climate(self):
        response = client.get("/plants/by_climate/?description=wet tropical")
        assert len(response.json()) == 3

    def test_get_plants_by_lifeform(self):
        response = client.get("/plants/by_lifeform/?description=tree")
        assert len(response.json()) == 1

    def test_get_taxons_by_taxon_rank(self):

        response = client.get("/taxons/by_taxon_rank/?taxon_rank=Subspecies")
        assert len(response.json()) == 2

        response = client.get("/taxons/by_taxon_rank/?taxon_rank=Genus")
        assert len(response.json()) == 1

        response = client.get("/taxons/by_taxon_rank/?taxon_rank=Species")
        assert len(response.json()) == 8

    def test_get_plants_by_continent(self):
        response = client.get("/plants/by_continent/?name=EUROPE")
        assert len(response.json()) == 4
        response = client.get("/plants/by_continent/?name=SOUTHERN AMERICA")
        assert len(response.json()) == 1

    def test_get_plant(self):
        create_fresh_db()
        response = client.get("/plant/2393672")
        assert response.json() == {
            "plant_name_id": 2393672,
            "reviewed": True,
            "ipni_id": "980294-1",
            "introduced": False,
            "extinct": False,
            "location_doubtful": False,
            "family_id": 1,
            "genus_id": 1,
            "taxon_id": 1,
            "publication_id": 1,
            "geographic_area_id": 1,
            "environmental_description_id": 1,
            "species_id": 1,
            "infraspecies_id": 1,
        }

    def test_delete_plant(self):
        create_fresh_db()
        response = client.delete("/plant/2393672")
        assert response.json() is True
        response = client.delete("/plant/2393672")
        assert response.json() is False
        response = client.delete("/plant/9999999")
        assert response.json() is False
