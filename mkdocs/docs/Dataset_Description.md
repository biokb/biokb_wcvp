# The contents of dowloaded wcvp data

### wcvp_names.csv [download wcvp.zip](https://sftp.kew.org/pub/data-repositories/WCVP/)

It provides detailed taxonomic, geographic, and publication information for vascular plants

1. **`plant_name_id`** :
   Unique identifier for each plant name in the WCVP database.
2. **`ipni_id`** :
   Identifier linked to the International Plant Names Index (IPNI), used to track plant name publications.
3. **`taxon_rank`** :
   The rank of the taxon, e.g., Species, Subspecies, or Variety.
4. **`taxon_status`** :
   The status of the taxon, e.g., Accepted or Synonym.
5. **`family`** :
   The family to which the plant belongs (e.g., Asteraceae, Rosaceae).
6. **`genus_hybrid`** :
   Indicates if the genus is a hybrid (denoted with a symbol or value).
7. **`genus`** :
   The genus name of the plant.
8. **`species_hybrid`** :
   Indicates if the species is a hybrid (denoted with a symbol or value).
9. **`species`** :
   The species name of the plant.
10. **`infraspecific_rank`** :
    The rank below species, e.g., subspecies (subsp.) or variety (var.).
11. **`infraspecies`** :
    The name of the infraspecific entity.
12. **`parenthetical_author`** :
    The author who first described the taxon, placed in parentheses if the name has been reclassified.
13. **`primary_author`** :
    The author(s) responsible for the current accepted name or reclassification.
14. **`publication_author`** :
    Author(s) associated with the publication of the name.
15. **`place_of_publication`** :
    The name of the publication where the taxon was first described.
16. **`volume_and_page`** :
    The volume and page number of the publication.
17. **`first_published`** :
    The year the taxon name was first published.
18. **`nomenclatural_remarks`** :
    Additional remarks related to nomenclature.
19. **`geographic_area`** :
    The geographic distribution of the taxon.
20. **`lifeform_description`** :
    Description of the plant's lifeform, e.g., subshrub, climber, perennial.
21. **`climate_description`** :
    Climate conditions where the taxon occurs, e.g., subtropical, temperate, desert.
22. **`taxon_name`** :
    The full scientific name of the taxon.
23. **`taxon_authors`** :
    The authorship of the taxon, typically including both parenthetical and primary authors.
24. **`accepted_plant_name_id`** :
    Identifier for the accepted name of the taxon, if the current entry is a synonym.
25. **`basionym_plant_name_id`** :
    Identifier for the basionym, the original name on which the current name is based.
26. **`replaced_synonym_author`** :
    Author of the synonym that has been replaced by the current name.
27. **`homotypic_synonym`** :
    Indicates whether the synonym is homotypic (denoted with** **`T`).
28. **`parent_plant_name_id`** :
    Identifier for the parent plant if the taxon is part of a hybrid formula or infraspecific rank.
29. **`powo_id`** :
    Identifier for the Plants of the World Online (POWO) database entry.
30. **`hybrid_formula`** :
    Formula describing the hybrid composition, if applicable.

### wcvp_distribution.csv

To describe the geographical distribution of plant taxa, with additional attributes about their presence, introduction, extinction, or uncertainty. Below is a description of each column in this dataset:

1. **`plant_locality_id`** :
   A unique identifier for each record of a plant's locality.
2. **`plant_name_id`** :
   Identifier linking the locality record to the corresponding plant in the main dataset, which contains plant taxonomic details.
3. **`continent_code_l1`** :
   A numerical code representing the continent.
4. **`continent`** :
   The name of the continent (e.g., SOUTHERN AMERICA).
5. **`region_code_l2`** :
   A numerical code representing the region within the continent.
6. **`region`** :
   The name of the region (e.g., Central America, Northern South America, Western South America).
7. **`area_code_l3`** :
   A code representing the specific area within the region.
8. **`area`** :
   The name of the area (e.g., Costa Rica, Venezuela, Bolivia, Colombia).
9. **`introduced`** :
   A binary indicator (0 or 1) denoting whether the plant has been introduced to the area (1 = Introduced, 0 = Native).
10. **`extinct`** :
    A binary indicator (0 or 1) indicating whether the plant is extinct in the area (1 = Extinct, 0 = Not Extinct).
11. **`location_doubtful`** :
    A binary indicator (0 or 1) specifying whether the plant's presence in the area is uncertain or doubtful (1 = Doubtful, 0 = Not Doubtful).

---

### wcvp_taxon.csv (from wcvp_dwca) [download wcvp_dwca.zip](https://sftp.kew.org/pub/data-repositories/WCVP/)

This dataset contains detailed taxonomic and ecological information for various plant taxa, emphasizing taxonomic details, publication references, geographic distribution, and ecological traits.

1. **`taxonid`** :
   Unique identifier for the taxon in the database.
2. **`family`** :
   The botanical family to which the taxon belongs (e.g., Polypodiaceae, Crassulaceae).
3. **`genus`** :
   The genus name of the taxon.
4. **`specificepithet`** :
   The specific epithet of the taxon, completing the species name when combined with the genus.
5. **`infraspecificepithet`** :
   The infraspecific name, if applicable (e.g., subspecies or variety). Empty if not relevant.
6. **`scientificname`** :
   The full scientific name of the taxon.
7. **`scientificnameauthorship`** :
   The author(s) who described or reclassified the taxon.
8. **`taxonrank`** :
   The taxonomic rank of the taxon (e.g., Species).
9. **`taxonomicstatus`** :
   Status of the taxon, e.g., "Accepted" if it is a valid name.
10. **`acceptednameusageid`** :
    Identifier for the accepted name of the taxon. Matches** **`taxonid` if the taxon is accepted.
11. **`parentnameusageid`** :
    Identifier for the parent taxon, linking the taxon to a higher taxonomic level.
12. **`originalnameusageid`** :
    Identifier for the original name usage, which could represent the basionym or synonym.
13. **`namepublishedin`** :
    Citation of the publication where the taxon was first described or revised (e.g., "Index Filic.: 306 (1905)").
14. **`nomenclaturalstatus`** :
    Status in nomenclature, if any (e.g., basionym, replaced synonym). Empty if not applicable.
15. **`taxonremarks`** :
    Additional remarks about the taxon, such as geographic distribution or other noteworthy traits.
16. **`scientificnameid`** :
    Identifier linking to external databases, e.g., IPNI (International Plant Names Index).
17. **`dynamicproperties`** :
    A JSON field containing dynamic ecological and distributional properties, including:

* `powoid`: Identifier for Plants of the World Online (POWO).
* `lifeform`: Plant lifeform (e.g., epiphyte, succulent, climbing shrub).
* `climate`: Climate where the taxon is found (e.g., wet tropical, temperate).
* `homotypicsynonym`: Notes on homotypic synonyms, if any.
* `hybridformula`: Hybrid composition, if applicable.
* `reviewed`: Indicates if the record has been reviewed (`Y` for yes,** **`N` for no).

18. **`references`** :
    A URL pointing to the detailed taxon page on the Plants of the World Online (POWO) database.

### wcvp_distribution.csv (from wcvp_dwca)

This dataset captures information about the geographic distribution, establishment means, and status of plant occurrences in various regions.

**Data Description**

1. **`coreid`** :
   A unique identifier for the taxonomic record or core entity linked to this geographic and status information.
2. **`locality`** :
   The name of the geographic region or locality where the taxon occurs (e.g., "Argentina Northeast," "Bolivia").
3. **`establishmentmeans`** :
   Describes how the taxon was established in the locality. This could include values such as:

* **`Native`** : Indicates the taxon is indigenous to the region.
* **`Introduced`** : Indicates the taxon was introduced by human activity.
* **`Cultivated`** : Indicates the taxon is grown intentionally in the region.
* Empty if no information is provided.

4. **`locationid`** :
   A standardized code (e.g., "TDWG:BOL") representing the geographic location. This often follows the TDWG (Taxonomic Databases Working Group) geographic region coding standard.
5. **`occurrencestatus`** :
   The occurrence status of the taxon in the locality, which may include:

* **`Present`** : The taxon is currently found in the region.
* **`Absent`** : The taxon is not found in the region.
* Empty if no information is provided.

6. **`threatstatus`** :
   The conservation or threat status of the taxon in the locality, potentially including categories such as:

* **`Endangered`**
* **`Critically Endangered`**
* **`Least Concern`**
* Empty if no information is provided.

 **Explanation of Data Usage**

* **Geographic Distribution Analysis** : The** **`locality` and** **`locationid` columns provide precise information on where a taxon is found, useful for mapping distributions.
* **Conservation Efforts** : The** **`threatstatus` column highlights regions where conservation actions may be needed.
* **Invasive Species Tracking** : The** **`establishmentmeans` column helps identify whether a taxon is native or introduced, aiding studies on invasive species.

### wcvp_replacementNames.csv (from wcvp_dwca)

to document relationships between taxonomic names, specifically focusing on replacement names and related nomenclatural remarks.

**Data Description**

1. **`taxonid`** :
   The unique identifier for the taxon in the database that has been replaced or linked to a related name.
2. **`relatednameusageid`** :
   The unique identifier for the related taxon name that serves as a replacement or is otherwise linked to the** **`taxonid`.
3. **`relationtype`** :
   Describes the type of relationship between the two names. In this dataset, the relation is "replacement name," indicating that the** **`relatednameusageid` is the taxonomic name that replaces the** **`taxonid`.
4. **`remarks`** :
   Additional remarks about the relationship, providing context or clarification. Examples include:

* **`not validly publ.`** : Indicates that the replacement name was not validly published.
* **`nom. illeg.`** : Indicates that the replacement name is nomenclaturally illegitimate.

 **Explanation of Data Usage**

* **Tracking Nomenclatural Changes** : This dataset provides a way to trace replacement names, which are critical for understanding the history and evolution of plant nomenclature.
* **Validating Taxonomic Names** : The remarks column highlights potential issues with validity or legitimacy, aiding taxonomists in ensuring proper use of names.
* **Database Cross-Referencing** : The** **`taxonid` and** **`relatednameusageid` columns enable linking to other records, allowing for comprehensive taxonomic reviews.
