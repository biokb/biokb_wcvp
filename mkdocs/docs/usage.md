## API Query Examples

---

Once the application is up and running, you can interact with the FastAPI interface by executing different queries to retrieve and manipulate vascular plants information. Below are some example queries that demonstrate how to load data, retrieve plant details, and explore taxon relationships.


#### `Load DB from CSV`


Load a test database from a local file located at `tests/data/test_data/test_data.csv`. This is a test_data combines wcvp_names.csv and wcvp_distribution.csv from [WCVP](https://sftp.kew.org/pub/data-repositories/WCVP/)

#### `Get Plants by ID`


Retrieve a Plant entity using its unique plant_name_id. For example, to retrieve information for the taxon ***Picramnia polyantha*** with `2549024`.

#### `Get Plants by Family`

Obtain all plants of a family using its family name. For example, to get all plants of the family ***Oxalidaceae*** with family name.

#### `Get Plants by Extinction`


Retrive all plants based on extinction state. For example, tp get all non-extinction plants with `extinction=0`.

#### `Get Plants by Continent`


Retrive all plants based on Geographic area. For example, tp get all plants from `EUROPE` with `name=EUROPE` under this function.




## MySQL Query Examples in phpMyAdmin

---

Use phpMyAdmin to execute MySQL queries and interact with your database. Below are example MySQL queries you can use in phpMyAdmin to interact with your vascular plants database.

1. Go to the SQL Tab.
2. Paste the following queries.
3. Click go.

#### `Retrieve All Plants in a Specific Family`

To retrieve all plants belonging to a specific family (e.g., **Oxalidaceae**):

```php
SELECT *
FROM plants
WHERE family = 'Oxalidaceae';
```

#### `Find Plants by Taxonomic Rank`

To retrieve all plants with a specific taxonomic rank (e.g., **species**):

```php
SELECT *
FROM plants
WHERE taxon_rank = 'species';
```

#### `Get Plants by Geographic Area`

To retrieve all plants from a specific geographic area (e.g., **Europe**):

```php
SELECT *
FROM plants
WHERE geographic_area = 'Europe';
```

#### `Retrieve Plants with a Specific Infraspecies`

To find plants with a specific infraspecies (e.g., **gracilispina**)

```php
SELECT *
FROM plants
WHERE infraspecies = 'gracilispina';
```

#### `Get Plants by Continent and Region`

To retrieve plants from a specific continent and region (e.g., **Europe and Northern Europe**):

```php
SELECT *
FROM plants
WHERE continent = 'Europe' AND region = 'Northern Europe';
```
