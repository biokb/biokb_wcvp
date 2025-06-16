# WCVP

The `project_group_1` package is a powerful tool for managing and analyzing vascular plants data from WCVP. It provides an intuitive interface for data owners to interact with and process plant information, offering structured access to taxon hierarchies, relationships, and classifications. This package supports data integration and analysis for various research applications.

### Key Features

- **Load WCVP Data:** Import data from local wcvp files.
- **MySQL Storage:** Efficiently manage data in a MySQL database.
- **phpMyAdmin Access:** Interact with data via phpMyAdmin.
- **FastAPI Interface:** Use FastAPI for API interactions.
- **Plant Information Retrieval:** Get detailed plant information.
- **Plant Management:** Manage taxons and plants in the database.
- **Descriptive Statistics:** Generate statistics on plant data.

For a detailed installation, usage, and literature, please refer to the [Full Documentation](/project-group-1/mkdocs/docs) .

For a comprehensive overview of the research motivation, methodology, data analysis, and conclusions, please refer to the Project Report

## Installation

### Step 1: Download the Project

```bash
$ git clone git@gitlab.informatik.uni-bonn.de:proglab-ii-24/projects/project-group-1.git
```

### Step 2: Install Dependencies

```bash
$ pdm install
```

### Step 3: Build the Image

```bash
$ podman build -t wcvp_image .
```

### Step 4: Start the Project

Ensure your Docker containers are running by executing the following command:

```bash
$ podman-compose up
```

This will start the following services:

- **MySQL:** The database server.
- **phpMyAdmin:** A web-based interface for managing MySQL.
- **FastAPI:** The API server for interacting with the data.

### Step 5: Access phpMyAdmin

1. Open your web browser and navigate to the phpMyAdmin interface:

[http://localhost:8080]

2. Log in to phpMyAdmin using the following credentials:

Username: db_user (as configured)

Password: db_passwd

3. Create a new database named `''db_name'' (for example)`:

```php
   CREATE DATABASE db_name;
```

4. Now, you can import data in to your newly created database

### Step 6: Test the API (Optional)

1. Set the environment variable:

```bash
  export CONNECTION_STR="sqlite:///dbs/fastapi.db"
```

2. Launch FastAPI:

```bash
  fastapi dev src/project_group_1/main.py
```

3. Open [http://localhost:8000](http://localhost:8000)

## API Query Examples

---

Once the application is up and running, you can interact with the FastAPI interface by executing different queries to retrieve and manipulate vascular plants information. Below are some example queries that demonstrate how to load data, retrieve plant details, and explore taxon relationships.

---

#### `Load DB from CSV`

---

Load a test database from a local file located at `tests/data/test_data/test_data.csv`. This is a test_data combines wcvp_names.csv and wcvp_distribution.csv from [WCVP](https://sftp.kew.org/pub/data-repositories/WCVP/)

#### `Get Plants by ID`

---

Retrieve a Plant entity using its unique plant_name_id. For example, to retrieve information for the taxon **_Picramnia polyantha_** with `2549024`.

#### `Get Plants by Family`

---

Obtain all plants of a family using its family name. For example, to get all plants of the family **_Oxalidaceae_** with family name.

#### `Get Plants by Extinction`

---

Retrive all plants based on extinction state. For example, tp get all non-extinction plants with `extinction=0`.

#### `Get Plants by Continent`

---

Retrive all plants based on Geographic area. For example, tp get all plants from `EUROPE` with `name=EUROPE` under this function.

---

## MySQL Query Examples in phpMyAdmin

Use phpMyAdmin to execute MySQL queries and interact with your database. Below are example MySQL queries you can use in phpMyAdmin to interact with your vascular plants database.

1. Go to the SQL Tab.
2. Paste the following queries.
3. Click go.

### Retrieve All Plants in a Specific Family

To retrieve all plants belonging to a specific family (e.g., **Oxalidaceae**):

```php
SELECT *
FROM plants
WHERE family = 'Oxalidaceae';
```

### Find Plants by Taxonomic Rank

To retrieve all plants with a specific taxonomic rank (e.g., **species**):

```php
SELECT *
FROM plants
WHERE taxon_rank = 'species';
```

### Get Plants by Geographic Area

To retrieve all plants from a specific geographic area (e.g., **Europe**):

```php
SELECT *
FROM plants
WHERE geographic_area = 'Europe';
```

### Retrieve Plants with a Specific Infraspecies

To find plants with a specific infraspecies (e.g., **gracilispina**)

```php
SELECT *
FROM plants
WHERE infraspecies = 'gracilispina';
```

### Get Plants by Continent and Region

To retrieve plants from a specific continent and region (e.g., **Europe and Northern Europe**):

```php
SELECT *
FROM plants
WHERE continent = 'Europe' AND region = 'Northern Europe';
```

# TODO: change README

Thanks to students of ....
{name = "MARIA MARTINEZ", email = "s0mamart@uni-bonn.com"},
{name = "Xiaoxuan Yu", email = "s04xyu@uni-bonn.de"},
{name = "Samana Fatima", email = "S22sfati@uni-bonn.de"},
