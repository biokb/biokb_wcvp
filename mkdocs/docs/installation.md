## Installation

This guide provides instructions on how to install and start the project using either the full project download or the Docker Compose method.

---

Follow these steps if you prefer to download the entire project and install the dependencies manually.

### Step 1: Download the Project from GitLab

---

To get started, download the entire project from GitLab:

```bash
$ git clone git@gitlab.informatik.uni-bonn.de:proglab-ii-24/projects/project-group-1.git
```

### Step 2: Install Dependencies

---

Install the project dependencies using **PDM** (Python Development Master):

```bash
$ pdm install
```

### Step 3: Build the Image Locally

---

- To build the image locally using **Podman**:

```bash
$ podman build -t wcvp_imgage .
```

### Step 4: Start the Project

---

To start the project using **Podman Compose**, run:

```bash
$ podman-compose up
```

This will start all the services defined in your `docker-compose.yaml` file.

### Step 5: Test the API Locally (Optional)

---

After downloading the project, you can launch the API as a standalone application. Follow these steps:

1. Set the required environment variable for the database connection:

   ```bash
   export CONNECTION_STR="sqlite:///dbs/fastapi.db"
   ```
2. Launch the FastAPI application:

   ```bash
   fastapi dev src/project_group_1/main.py
   ```
3. Open your browser and navigate to the FastAPI interface:

   [http://localhost:8000](http://localhost:8000)
