/* Create table with nodes */

CREATE TABLE nodesdk AS SELECT * FROM planet_osm_nodes;

ALTER TABLE nodesdk 
ADD COLUMN latitude DECIMAL, 
ADD COLUMN longitude DECIMAL;

UPDATE nodesdk SET longitude = lon::decimal/10000000, latitude = lat::decimal/10000000;

ALTER TABLE nodesdk ADD COLUMN geometry geometry(Point, 4326);
UPDATE nodesdk SET geometry = ST_SetSRID(ST_MakePoint(longitude, latitude), 4326);
ALTER TABLE nodesdk ALTER COLUMN geometry TYPE geometry(POINT,25832) USING ST_Transform(geometry,25832);
