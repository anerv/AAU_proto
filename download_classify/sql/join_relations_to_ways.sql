/*
This script creates a spatail join between cycling routes and roads/bike lanes
Update table names as needed
*/


CREATE MATERIALIZED VIEW buffer AS 
    (SELECT r.name, r.operator, r.ref, r.route, ST_Buffer(geometry, 1, 'endcap=round join=round') AS geometry
    FROM relkbh r);

CREATE INDEX buffer_geom_idx
  ON buffer
  USING GIST (geometry);

SELECT w.osm_id, w.road_type, w.cycling_infrastructure, w.geometry, 
    b.name, b.operator, b.ref, b.route, b.geometry FROM wayskbh w JOIN buffer b ON
	ST_ContainsProperly(b.geometry,w.geometry)
	WHERE b.route = 'bicycle' ORDER BY osm_id;

-- Use STRUCT??
CREATE VIEW ways_rel AS (SELECT w.osm_id, ARRAY_AGG(b.name ORDER BY b.name) AS name, ARRAY_AGG(b.operator ORDER BY b.name) AS operator, ARRAY_AGG(b.ref ORDER BY b.name) AS ref 
	FROM wayskbh w JOIN buffer b ON
	ST_ContainsProperly(b.geometry,w.geometry)
	WHERE b.route = 'bicycle' GROUP BY osm_id);

ALTER TABLE wayskbh 
	ADD COLUMN route_name VARCHAR, 
	ADD COLUMN route_operator VARCHAR, 
	ADD COLUMN route_ref VARCHAR;

UPDATE wayskbh w SET route_name = r.name, route_operator = operator, route_ref = r.ref 
    FROM ways_rel r WHERE w.osm_id = r.osm_id;

DROP VIEW ways_rel;
DROP MATERIALIZED VIEW buffer;
