# AAU Cykeldata

This repository contains Python and SQL scripts for creating a Postgresql-database with data from OpenStreetMap, with a focus on cycling infrastructure.

The repository has been developed by [Aalborg University, Institute for Planning](https://www.plan.aau.dk/).
Thanks to [People for Bikes](https://peopleforbikes.org/) for initial inspiration for how to work with OSM-data.

## Objectives
The purpose is to reclassify and simplify OSM data and the sometimes high number of tags to a simpler format, which is easier to query, analyse and visualise.
Furthermore OSM-data is enriched or validated using open data from public institutions.


## Usage
The repository contains to methods for loading OSM data to the database: The Python module osmnx and the command line tool osm2pgsql.
Using osm2pgsql is recommended, since it results in richer data (including for example relations).
If osmnx is used, use the files *download_osm_data.py* and *prep_classify_osmn.py*. 
If osm2pgsql is used (see *loading_osm.sql*) the scripts *prep_osm_data_osm2pgsql.py* and *classify_osm2pgsql.py* must be used.

Update info in *config.py* with the necessary info about database, name of study area etc.

It is assumed that a postgresql database has been created with the necessary extensions (see *loading_osm.sql*).
A number of Python modules such as geopandas, sqlalchemy, psycopg2 must be installed before use.


## License
OpenStreetMap® is open data, licensed under the [Open Data Commons Open Database License](https://www.openstreetmap.org/copyright).
Remember to credit OSM whenever data is used.


If you have any questions (or need help with the Danish terminology) feel free to reach out!


## TO-DO
- Add document describing re-classification method
- Fix how highway type is reclassified/translated to the Danish road types so it matches official road types




