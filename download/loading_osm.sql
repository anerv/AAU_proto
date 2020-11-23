/*
These commands creates a database using psql (SQL shell) and loads an osm file into it using the standard command prompt
OSM-files can be downloaded from BBbike, GeoFabrik etc.
Assumes that osm2pgsql is installed along with PostgreSQL and PostGIS.
Adapt file paths as needed.

Here a modified style file is used to get all relevant tags as individual columns (see this repo for style file)
*/

CREATE DATABASE osmbike;
\CONNECT osmbike;
CREATE EXTENSION postgis;
CREATE EXTENSION postgis_topology;
CREATE EXTENSION hstore;

--Copenhagen
osm2pgsql -c -d osmbike -U postgres -H localhost -W -S "C:\Users\viero\OneDrive\Documents\AAU\AAU_prototype\download\modified_stylefile.style" "C:\Users\viero\OneDrive\Documents\AAU\AAU_prototype\download\copenhagen.osm.pbf"