# **The World Checklist of Vascular Plants:  A Resource for Global Plant Diversity**

Developing interoperable Python libraries for loading, querying, and analyzing ethnobotanicaldata from multiple resources using WCVP database

**Authors**: Xiaoxuan Yu, Samana Fatima, Vaishnavee Thote, and Maria Martinez

28/02/2025

## **Abstract**

This project develops a Python library within a multi-container Docker setup to manage and analyze data from the World Checklist of Vascular Plants (WCVP). It facilitates WCVP data management via MySQL and phpMyAdmin, offering a FastAPI interface for querying and analyzing plant information. Key features include plant retrieval, taxon management, and statistical analysis, with a focus on interoperability using unique identifiers. The containerized architecture ensures portability and scalability, making it a versatile tool for biodiversity researchers.

## **Introduction**

The World Checklist of Vascular Plants (WCVP), developed by the Royal Botanic Gardens, Kew, is a comprehensive, globally curated database documenting over 1.38 million plant names, including 342,953 accepted species. It serves as a critical resource for biodiversity research, conservation, and policy implementation by integrating data from the International Plant Names Index (IPNI), herbaria, literature, and expert reviews.

Unlike other databases, WCVP undergoes rigorous expert validation, receives dynamic weekly updates, and adheres to international nomenclatural standards. It supports initiatives like the Global Biodiversity Information Facility (GBIF) and has been instrumental in research efforts such as Indonesia’s vascular plant checklist, which identified 30,466 native species.

Despite its strengths, WCVP faces challenges, including gaps in geographic distribution data and regional taxonomic inconsistencies, particularly in tropical ecosystems. To address these, WCVP continues to expand collaborations with botanical institutions, refine taxonomic reconciliation workflows, and enhance data validation. Strengthening these efforts is crucial to maintaining WCVP’s role as a foundational global plant database.

## **Major Milestones and Gaps in Current Research**

**Key Milestones:**

* The development of standardized workflows for taxonomic reconciliation and data validation in WCVP
* The creation of a region specific vascular plant checklist in Indonesia, addressing local biodiversity hotspots and endemic species
* Ethnopharmacological research into vascular plant genera, revealing potential applications in medicine andsustainable development

**Significant Gaps:**

* Geographic data coverage is limited in tropical and underrepresented regions, affecting conservation planning
* Variations in taxonomic expertise and unresolved species concepts pose challenges to achieving globalconsensus
* Limited research on the phytochemistry and pharmacological potential of vascular plants restricts broader applications

## **Methodology**

#### **System Architecture**

The software follows a modular architecture, designed to handle real WCVP (World Checklist of Vascular Plants) data efficiently. The architecture supports structured data processing, robust API interactions, and reliable deployment. Each layer contributes to the overall scalability and performance of the application.

### 1. **Data Processing: Pandas and SQLAlchemy for Managing Dataset Imports**

The data processing phase involved preparing the WCVP dataset for integration into a MySQL database. The process ensured data cleanliness, consistency, and proper structuring for efficient querying and analysis.

**1.1 Dataset Analysis and Cleaning:**

* Each WCVP dataset was analyzed and cleaned using  **Pandas.**
* Duplicates were removed, and missing or inconsistent values were handled by replacing `NaN` values with appropriate defaults (e.g., `"Unknown"` for text fields and `0` for boolean flags).
* Columns were individually checked for duplicates and cleaned to ensure data integrity.

**1.2 Database Schema Design:**

* Two main tables were designed:
  * **wcvp_names:** Stores taxonomic and nomenclatural data for plant species.
  * **wcvp_distributions:** Contains distribution data for plant species.
* These tables were merged into a single file,  **test_data.csv** , for testing and validation.

**1.3 Data Integration:**

* **SQLAlchemy** was used to manage database interactions, including table creation, data insertion, and querying.
* A **DbManager** class was implemented to handle database operations, such as creating/dropping tables and importing data.
* The `get_or_create` method ensured efficient handling of database entries by either fetching existing records or creating new ones.

**1.4 Data Import:**

* The cleaned dataset was imported into the MySQL database using SQLAlchemy.
* Each row of the dataset was processed to:
  * Fetch or create related entities (e.g., Family, Genus, Species, Taxon).
  * Handle date formatting and missing values.
  * Link entities (e.g., linking a plant to its family, genus, and geographic area).
* Rows with missing critical fields (e.g., `plant_name_id`, `family`, `genus`, `species`) were skipped to maintain data quality.

### 2. **Database Layer: SQLAlchemy ORM with SQLite/MySQL**

The database layer utilizes SQLAlchemy ORM to define and manage the database schema, ensuring data consistency and integrity across the application.

**2.1 Database Structure and Relationships:**

To ensure an organized and efficient representation of plant-related data, an Entity-Relationship (ER) diagram was developed. This diagram offers a visual overview of the database structure, illustrating key entities, attributes, and relationships:

![Diagram - Data Schema](imgs/data_schema.png)
*Figure 1: Data Schema*

* Taxonomic classification is represented through hierarchical associations among family, genus, species, and infraspecies.
* Geographical distribution is structured across multiple levels, including continent, region, area, and geographic area.
* Taxonomic attributes such as taxon, taxon rank, and taxon status provide detailed classification information.
* Environmental descriptors, including climate, lifeform, and general environmental conditions, help contextualize plant habitats.
* Infraspecies classification and publication records support further scientific documentation and research validation.

This relational model ensures a comprehensive and structured framework for storing, managing, and analyzing plant-related data efficiently.

**2.2 Key Scripts:**

- **models.py:** Defines the database schema, including table structures, fields, and relationships.
- **manager.py:** Manages core business logic, handling data retrieval, updates, and interactions between the API and the database.
- **test_software.py:** Contains unit tests and integration tests to validate database operations, ensuring reliable performance.

**2.3 Database Management Systems:**

- **SQLite:** Used during initial development for its simplicity.
- **MySQL** : Adopted for final deployment due to its scalability, robust query capabilities, and structured data management.

**2.4 Key Tools and Libraries**

* **Pandas:** For data cleaning, transformation, and analysis.
* **SQLAlchemy:** For database schema management and data insertion.
* **Python:** For scripting the entire data processing pipeline.

### 3. **API Layer: FastAPI for Handling Data Requests**

The API layer is built using FastAPI, providing a fast, reliable, and interactive interface for database interactions.

**3.1 Core Functionality:**

- FastAPI supports asynchronous processing, improving performance and responsiveness.
- Automatic generation of interactive documentation (Swagger UI) facilitates user exploration of available endpoints.

**3.2 Key Components:**

- **main.py**: Launches the FastAPI application and defines API routes.
- **schemas.py**: Specifies Pydantic models for request validation and response formatting, ensuring data consistency.
- **tags.py**: Organizes and categorizes API endpoints for clearer navigation and management.
- 

**3.3 API Testing:**

- **test_api.py** validates the robustness of API endpoints by checking response correctness, data retrieval, submission functionalities, and error-handling mechanisms.

This API structure ensures efficient and secure user interactions with the WCVP database.

### 4. **Deployment: VS Code and Docker for Containerization**

The deployment process was designed for scalability, portability, and consistent performance using VS Code and Docker.

**4.1 Development Environment:**

- VS Code was used as the primary development environment, providing powerful tools for coding, debugging, and version control.

**4.2 Containerization with Docker:**

- Docker ensures that the application runs consistently across different environments.
- **Dockerfile**: Defines the environment configuration and dependencies required to run the application.
- **docker-compose.yml**: Orchestrates the deployment of multiple containers, including the FastAPI application, MySQL database, and phpMyAdmin.

**4.3 Database Management with phpMyAdmin:**

- **phpMyAdmin** was integrated as a web-based interface for managing the MySQL database.
- It facilitated SQL query execution, data inspection, and debugging, enabling real-time management of the database during development and testing.

**4.4 API Documentation and Testing**

The FastAPI framework provides interactive API documentation through two interfaces:

- **Swagger UI**: Accessible at `/docs`, this interface allows to test API endpoints in real-time and explore available routes interactively [(https://localhost:8080/docs)] .
- **MySQL client**: Connect to the MySQL database using the command:

```python
  mysql -u db_user -p db_passwd -h 127.0.0.1 -P 3307
```

- **phpMyAdmin**: Manage the MySQL database through the web-based interface at [(http://localhost:8081)].

## **Analysis and results**

The analysis of the taxonomic database system focused on evaluating the performance, data integrity, and usability of the API. Various tests were conducted to assess the efficiency of data retrieval, the correctness of database migrations from SQLite to MySQL, and the effectiveness of the implemented validation mechanisms.

![Dataset Overview](imgs/missing_values.png)

The graph illustrates the number of missing values for each column in the database, revealing a clear trend. Several columns, appearing at the left of the graph, such as *homotypic_synonym, genus_hybrid, species_hybrid, hybrid_formula, and replaced_synonym_author*, contain the highest amount of missing data, making them less reliable for analysis. Conversely, columns like *taxon_name, genus, family, continent, and region* have significantly fewer missing values, suggesting they are more complete. These columns were prioritized for analysis because well-populated columns will yield more accurate and meaningful results

![Dataset Overview](imgs/species_distribution.png)

The choropleth map illustrates the species distribution by area based on the WCVP database. Regions with higher species counts are represented in yellow and orange, indicating biodiversity hotspots, particularly in parts of South America, Africa, and Australia. Conversely, areas shaded in dark purple have lower species counts. It is important to notice that certain regions appear gray, which suggests a lack of data rather than an absence of species. These gaps might be caused due to data unavailability for those specific locations in the database.

<!-- ![Dataset Overview](imgs/family_distribution.png) -->

<!-- ![Dataset Overview](imgs/introduced_extint.png) -->

<figure>
  <img src=imgs/introduced_extint.png alt="Image description">
  <figcaption> Figure 3. Relationship between the number of introduced species and extinct species across different regions, group and labeled by continent .</figcaption>
</figure>

The positive trend line suggests a correlation, indicating that continents with a higher number of introduced species tend to have a greater number of extinct species. However, some continents, such as Antarctica, show very few introduced species and minimal extinctions, while others, like Northern America, have a high number of introduced species but a relatively lower extinction count compared to the trend line. The variability in data points suggests that factors beyond introduction alone—such as conservation efforts, ecosystem resilience, and human impact—may influence extinction rates differently across regions.

<figure>
  <img src=imgs/top_introduced1.png alt="Image description">
  <figcaption> Figure 4. This bar plot visualizes the 10 most common introduced species in the dataset, ranked by their number of occurrences.</figcaption>
</figure>

## Discussion

The development of this Python library and its integration into a multi-container Docker setup has effectively addressed several challenges and gaps identified in the WCVP database. By leveraging modern tools and technologies, the project has improved data accessibility, interoperability, and usability for researchers.

### 1. Addressing Gaps and Milestones

1. **Geographic Data Coverage:**

* The choropleth map analysis revealed significant gaps in species distribution data, particularly in tropical and underrepresented regions. While the project cannot directly fill these gaps, it provides a robust framework for integrating additional data sources in the future. The modular architecture and scalable database design make it easier to incorporate new datasets as they become available.

2. **Taxonomic Expertise and Species Concepts:**

* The standardized workflows implemented in the project, such as data cleaning and validation using Pandas and SQLAlchemy, help mitigate inconsistencies arising from regional variations in taxonomic expertise. The use of unique identifiers and structured data models ensures that species concepts are consistently applied across the database.

3. **User Accessibility:**

* The integration of phpMyAdmin and Swagger UI enhances user accessibility, enabling researchers to interact with the database and API without requiring advanced technical skills.

### 2. Limitations and Future Work

While the project has made significant strides, some limitations remain:

**Data Gaps:**

* The analysis revealed missing data in several columns, such as genus_hybrid (439,847 null values), species_hybrid (431,946 null values), and infraspecific_rank (384,857 null values). Geographic regions also showed gaps, particularly in tropical areas.
* To address this, a smaller test file (test_data.csv) was created for development and testing, as importing the full dataset posed challenges due to its size and complexity.
* Future work could focus on integrating additional data sources to fill these gaps and improve data completeness.

**Handling Large Datasets**

The sheer volume of data in the WCVP database presents significant challenges in storage, retrieval, and processing efficiency. During initial testing with the full dataset, we encountered slow query performance and memory constraints, which hindered the system's responsiveness. For example, queries involving complex joins or filtering operations took several minutes to execute, and memory usage often exceeded available resources, causing the application to crash.

To address these challenges, we adopted a **subset-based approach** for development and testing. A smaller, representative dataset (`test_data.csv`) was created, allowing us to refine the system's functionality without the overhead of processing the entire dataset. While this approach enabled faster iteration and testing, it also highlighted the need for robust performance optimization techniques to handle the full dataset in production.

## Conclusion

This project has successfully developed a Python library and multi-container Docker setup to manage and analyze WCVP data, addressing key challenges in biodiversity research. By combining modern tools like FastAPI, MySQL, and Pandas, the system provides a scalable, interoperable, and user-friendly platform for querying and analyzing vascular plant data.

The project’s contributions include:

**Improved Data Accessibility:** Through phpMyAdmin and Swagger UI, researchers can easily interact with the database and API.

**Enhanced Interoperability:** The use of unique identifiers and standardized workflows ensures compatibility with other datasets and systems.

**Scalability:** The containerized architecture supports future expansion and integration of additional data sources.

By addressing gaps in geographic data coverage, taxonomic expertise, and data integration, the project strengthens WCVP’s role as a cornerstone of global plant data infrastructure. It also lays the groundwork for future research, including ethnopharmacological studies and conservation planning.

## References

* Sun, J., Liu, B., Rustiami, H., Xiao, H., Shen, X., & Ma, K. (2024).  Mapping Asia plants:  Plant diversity anda checklist of vascular plants in Indonesia.Plants, 13(2281).https://doi.org/10.3390/plants13162281
* Samadd, Md.  A., Hossain, Md.  J., Zahan, M. S., Islam, Md.  M., & Rashid, M. A. (2024).  A comprehensiveaccount on ethnobotany, phytochemistry, and pharmacological insights of genus Celtis.Heliyon,10(4), e29707.https://doi.org/10.1016/j.heliyon.2024.e297072
* Govaerts, R. (Ed.). (2024). WCVP: World Checklist of Vascular Plants. Facilitated by the Royal Botanic Gardens, Kew. [Version 13]. https://doi.org/10.34885/nswv-8994
* Govaerts, R., Nic Lughadha, E., et al. (2021). The World Checklist of Vascular Plants, a continuously updated resource for exploring global plant diversity. Scientific Data, 8(215). https://doi.org/10.1038/s41597-021-00997-6
