/* Create table with nodes */

CREATE TABLE nodesdk AS SELECT * FROM planet_osm_nodes;

ALTER TABLE nodesdk 
ADD COLUMN latitude DECIMAL, 
ADD COLUMN longitude DECIMAL;

UPDATE nodesdk SET longitude = lon::decimal/10000000, latitude = lat::decimal/10000000;

ALTER TABLE nodesdk ADD COLUMN geometry geometry(Point, 4326);
UPDATE nodesdk SET geometry = ST_SetSRID(ST_MakePoint(longitude, latitude), 4326);
ALTER TABLE nodesdk ALTER COLUMN geometry TYPE geometry(POINT,25832) USING ST_Transform(geometry,25832);

_________

--clip to stud
y area
DELETE FROM nodesdk AS points WHERE lon < 0 OR lat < 0;

ALTER TABLE nodesdk 
ADD COLUMN latitude NUMERIC, 
ADD COLUMN longitude NUMERIC, 
ADD COLUMN lat1 VARCHAR, 
ADD COLUMN lat2 VARCHAR, 
ADD COLUMN long1 VARCHAR,
ADD COLUMN long2 VARCHAR;

UPDATE nodesdk SET longitude = lon/10000000, latitude = lat/10000000;

UPDATE nodesdk SET lat1 = substring(lat::text FROM 0 for 3), lat2 = substring(lat::text FROM 3 for 10);
UPDATE nodesdk SET long1 = substring(lon::text FROM 0 for 2), long2 = substring(lon::text FROM 2 for 10) WHERE substring(lon::text FROM 0 for 1) > 1;
UPDATE nodesdk SET long1 = substring(lon::text FROM 0 for 3), long2 = substring(lon::text FROM 3 for 10) WHERE substring(lon::text FROM 0 for 1) = 1;
UPDATE nodesdk SET latitude = (lat1||'.'||lat2)::NUMERIC; 
UPDATE nodesdk SET longitude = (long1||'.'||long2)::NUMERIC;

ALTER TABLE nodesdk ADD COLUMN geometry geometry(Point, 4326);
UPDATE nodesdk SET geometry = ST_SetSRID(ST_MakePoint(longitude, latitude), 4326);
ALTER TABLE nodesdk ALTER COLUMN geometry TYPE geometry(POINT,25832) USING ST_Transform(geometry,25832);

ALTER TABLE nodesdk DROP COLUMN lat1, DROP COLUMN lat2, DROP COLUMN long1, DROP COLUMN long2;


/*
CREATE VIEW sub AS (
	SELECT 
		id, substring(lat::text FROM 0 for 3) AS lat1, 
		substring(lat::text FROM 3 for 10) AS lat2 
	FROM nodesdk
);

ALTER TABLE nodesdk ADD COLUMN geometry geometry(Point, 4326);

UPDATE nodesdk SET geometry = ST_SetSRID(ST_MakePoint(lon, lat), 4326);

ALTER TABLE nodesdk ALTER COLUMN geometry TYPE geometry(POINT,25832) USING ST_Transform(geometry,25832);

SELECT * from nodesdk;
--SELECT lat, substring(lat::text FROM 0 for 3) AS lat1, substring(lat::text FROM 3 for 10) AS lat2 FROM nodesdk;
*/
/*CREATE VIEW sub AS (
	SELECT 
		id, substring(lat::text FROM 0 for 3) AS lat1, 
		substring(lat::text FROM 3 for 10) AS lat2 
	FROM nodesdk
); */
--ALTER TABLE nodesdk ADD COLUMN lat1 text, ADD column lat2 text;
--UPDATE nodesdk SET lat1 = substring(lat::text FROM 0 for 3), 
	--lat2 = substring(lat::text FROM 3 for 10);
		
--UPDATE nodesdk SET latitude = lat1||'.'||lat2; 
--FROM sub WHERE sub.id = nodesdk.id;

--SELECT substring(lat::text FROM 3 for 10) AS lat2 FROM nodesdk LIMIT 10;
--substring('Thomas' from 2 for 3)
