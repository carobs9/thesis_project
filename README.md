# Understanding the role of mobility in segregation patterns in the city of Madrid
Thesis project to understand the role of mobility in segregation patterns in the city of Madrid.

## Environment and Running Code

To run a Python script with specific environment (.venv): environment_path + .py path

Example: source /Users/caro/Desktop/thesis_project/.thesis_env/bin/activate

/Users/caro/Desktop/thesis_project/.thesis_env/bin/python /Users/caro/Desktop/thesis_project/segregation_indices/morans_i.py

Requirements:  pip install -r /Users/caro/Desktop/thesis_project/requirements.txt

## The data

This study analyzes the mobility of residents in Spain daily and hourly starting from January 1, 2022. It measures all trips with origin or destination within national territory (including trips to/from abroad).

The base zoning for the study consists of census districts and aggregations of these (in order to ensure compliance with current data protection regulations) for the territory of Spain, and NUTS-3 zones for France and Portugal, and 1 zone for other foreign countries. This zoning includes a total of 3,743 zones for the national territory, 117 zones for France and Portugal, and 1 zone for abroad, covering the rest of the world.

From this base zoning, two additional zonings are generated: one at the municipal level (including aggregations of municipalities for data protection) and another at the level of large urban areas (GAUs).

As a result, 3 analyses are generated: trips (viajes), overnight stays (pernoctaciones), and people (personas).

The results are published monthly (around the 15th of each month). They are available for the months from January 2022 onwards.

### Viajes Folder

This folder contains travel matrices by days and by full months, updated daily.

The master matrix 1 or travel matrix contains the number of trips and traveler-kilometers for each day and each combination of origin, destination, origin activity, destination activity, residence, time period, and distance (by ranges): date|origin|destination|origin_activity|destination_activity|residence|age|period|distance|trips|trips_km.

These are compressed text files with fields separated by '|' (vertical bar), and numeric values use '.' (dot) as the decimal separator. The "origin" and "destination" data refer to the district code or a grouping of these in the case of sparsely populated areas (zoning used and which can be downloaded as a Shapefile - file “zonificacion-distritos.zip”).