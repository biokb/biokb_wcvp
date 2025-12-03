# API for World Checklist of Vascular Plants (WCVP) Data

`biokb_wcvp` is a Python library provide a RESTfulAPI to query data from WCVP

## About WCVP

[World Checklist of Vascular Plants (WCVP)](https://www.gbif.org/dataset/f382f0ce-323a-4091-bb9f-add557f3a9a2) is a comprehensive, curated database maintained by the [Royal Botanic Gardens, Kew](https://www.kew.org/). It provides authoritative information on the accepted scientific names and synonyms of vascular plants worldwide.

## Installation

```bash
git clone git@github.com:biokb/biokb_wcvp.git
cd biokb_wcvp
uv venv
source .venv/bin/activate
uv pip install podman-compose
podman-compose -f docker-compose.db_neo.yml up -d
podman-compose up --build -d
```

Open http://localhost:8000/docs (perhaps there will be a delay, please reload after some seconds)
