/*
These commands creates a database using psql (SQL shell) and loads an osm file into it using the standard command prompt
OSM-files can be downloaded from BBbike, GeoFabrik etc.
Assumes that osm2pgsql is installed along with PostgreSQL and PostGIS.
Adapt file paths as needed.

Here a modified style file is used to get all relevant tags as individual columns (see this repo for style file)
*/

CREATE DATABASE rh;
\connect rh;
CREATE EXTENSION postgis;
CREATE EXTENSION postgis_topology;
CREATE EXTENSION hstore;
CREATE EXTENSION postgis_raster;

--Modify database information as needed
osm2pgsql -c -d rh -U postgres -H localhost -W -S "C:\Users\OA03FG\Aalborg Universitet\Urban Research group - General\AAU data\AAU grunddata\PROTOTYPE\AAU_proto\download_classify\modified_stylefile.style" --slim -K "C:\Users\OA03FG\Downloads\denmark-latest.osm.pbf"

-- Use command below to load raster to database
raster2pgsql -s 25832 -C -I -F -t 3741x3570 "C:\Users\OA03FG\Aalborg Universitet\Urban Research group - General\AAU data\AAU grunddata\PROTOTYPE\AAU_proto\download_classify\data/DHM_05.tif" public.dhm_05 | psql -h localhost -p 5432 -U postgres -d rh

--raster2pgsql -s 25832 -C -I -F -t 1406x839 "C:\Users\OA03FG\Aalborg Universitet\Urban Research group - General\AAU data\AAU grunddata\PROTOTYPE\AAU_proto\download_classify\data/DHM_test.tif" | psql -h localhost -p 5432 -U postgres -d rh
