/*
This script updates the attribute for ways data based on the land cover
*/
ALTER TABLE waysdk 
ADD COLUMN landscape VARCHAR, 
ADD COLUMN close_to VARCHAR;

CREATE MATERIALIZED VIEW ways_lc AS 
	SELECT w.osm_id, string_agg(l.label_modified, ', ') AS landcover FROM waysdk w 
    JOIN land_cover l ON ST_Intersects(w.geometry, l.geometry) GROUP BY osm_id;

CREATE INDEX osmid ON ways_lc (osm_id);

UPDATE waysdk w SET landscape = landcover
    FROM ways_lc lc WHERE w.osm_id = lc.osm_id;

CREATE MATERIALIZED VIEW ways_close_to AS
	SELECT w.osm_id, string_agg(l.label_modified, ', ') AS landcover FROM waysdk w 
	JOIN land_cover l ON ST_DWithin(w.geometry, l.geometry, 10) GROUP BY osm_id;

UPDATE waysdk SET close_to = landcover 
	FROM ways_close_to c WHERE w.osm_id = c.osm_id;

DROP VIEW ways_lc;
DROP VIEW ways_close_to;
/*
SELECT w.osm_id, l.label_modified FROM waysdk w 
    JOIN land_cover l ON ST_Intersects(w.geometry, l.geometry);


SELECT w.osm_id, ARRAY_AGG(b.name ORDER BY b.name) AS name, 
	ARRAY_AGG(b.operator ORDER BY b.name) AS operator, 
	ARRAY_AGG(b.ref ORDER BY b.name) AS ref 
	FROM waysdk w JOIN buffer b ON
	ST_ContainsProperly(b.geometry,w.geometry)
	WHERE b.route = 'bicycle' GROUP BY osm_id; */