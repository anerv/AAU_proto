/*
This scrip creates a database and loads a file into it.
Adapt file paths as needed

Here a modified style file is used to get all relevant tags as individual columns

*/

CREATE DATABASE osm_bike;
\CONNECT osm_bike;
CREATE EXTENSION postgis;
CREATE EXTENSION postgis_topology;
CREATE EXTENSION hstore;

--Copenhagen
osm2pgsql -c -d copenhagen -U postgres -H localhost -W -S "C:\Users\viero\OneDrive\Documents\AAU\AAU_prototype\download\modified_stylefile.style" "C:\Users\viero\OneDrive\Documents\AAU\AAU_prototype\download\copenhagen.osm.pbf"