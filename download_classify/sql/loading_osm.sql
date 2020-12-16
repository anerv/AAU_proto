/*
These commands creates a database using psql (SQL shell) and loads an osm file into it using the standard command prompt
OSM-files can be downloaded from BBbike, GeoFabrik etc.
Assumes that osm2pgsql is installed along with PostgreSQL and PostGIS.
Adapt file paths as needed.

Here a modified style file is used to get all relevant tags as individual columns (see this repo for style file)
*/

CREATE DATABASE osmbike;
\connect osmbike;
CREATE EXTENSION postgis;
CREATE EXTENSION postgis_topology;
CREATE EXTENSION hstore;

--Modify database information as needed
osm2pgsql -c -d dk -U postgres -H localhost -W -S "C:\Users\OA03FG\Aalborg Universitet\Urban Research group - General\AAU data\AAU grunddata\PROTOTYPE\AAU_proto\download_classify\modified_stylefile.style" --slim "C:\Users\OA03FG\Downloads\denmark-latest.osm.pbf"
