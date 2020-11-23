/*
This scrip creates a database and loads a file into it.
Adapt file paths as needed
*/

CREATE DATABASE osm;
\CONNECT osm;
CREATE EXTENSION postgis;
CREATE EXTENSION postgis_topology;
CREATE EXTENSION hstore;

-- Run code in files:
script\pgsnapshot_schema_0.6.sql

script\pgsnapshot_schema_0.6_linestring.sql

CREATE INDEX idx_nodes_tags ON nodes USING GIN(tags);
CREATE INDEX idx_ways_tags ON ways USING GIN(tags);
CREATE INDEX idx_relations_tags ON relations USING GIN(tags); 


C:\Users\viero\OneDrive\Documents\PROGRAMMING\osmosis-0.48.3\bin\osmosis --read-pbf file=C:\Users\viero\OneDrive\Documents\AAU\AAU_prototype\download\denmark-latest.osm.pbf --write-pgsql host="localhost" database="osm" user="postgres" password="IGEON20"


OneDrive\Documents\PROGRAMMING\osmosis-0.48.3\script\pgsnapshot_schema_0.6.sql


C:\Users\viero\OneDrive\Documents\PROGRAMMING\osmosis-0.48.3\bin\osmosis --read-pbf file=C:\Users\viero\OneDrive\Documents\AAU\AAU_prototype\download\hamburg-latest.osm.pbf --write-pgsql host="localhost" database="osm" user="postgres" password="IGEON20"


CREATE DATABASE osm_bike;
\CONNECT osm_bike;
CREATE EXTENSION postgis;
CREATE EXTENSION postgis_topology;
CREATE EXTENSION hstore;

--Copenhagen
osm2pgsql -c -d copenhagen -U postgres -H localhost -W -S "C:\Users\viero\OneDrive\Documents\AAU\AAU_prototype\download\modified_stylefile.style" "C:\Users\viero\OneDrive\Documents\AAU\AAU_prototype\download\copenhagen.osm.pbf"