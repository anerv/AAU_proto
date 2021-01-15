/*
This script creates a spatail join between cycling routes and roads/bike lanes
Update table names as needed
*/

CREATE MATERIALIZED VIEW buffer AS 
    (SELECT r.name, r.operator, r.ref, r.route, ST_Buffer(geom, 1, 'endcap=round join=round') AS geom
    FROM rel_rh r);

CREATE INDEX buffer_geom_idx
  ON buffer
  USING GIST (geom);

/*
SELECT w.osm_id, w.road_type, w.cycling_infrastructure, w.geom, 
    b.name, b.operator, b.ref, b.route, b.geom FROM ways_rh w JOIN buffer b ON
	ST_ContainsProperly(b.geom,w.geom)
	WHERE b.route = 'bicycle' ORDER BY osm_id; */


CREATE VIEW ways_rel AS (SELECT w.osm_id, ARRAY_AGG(b.name ORDER BY b.name) AS name, 
	ARRAY_AGG(b.operator ORDER BY b.name) AS operator, 
	ARRAY_AGG(b.ref ORDER BY b.name) AS ref 
	FROM ways_rh w JOIN buffer b ON
	ST_ContainsProperly(b.geom,w.geom)
	WHERE b.route = 'bicycle' GROUP BY osm_id);

/*
-- Use STRUCT instead?
CREATE VIEW ways_rel2 AS 
	(SELECT MIN(w.osm_id) AS id_, ARRAY_AGG(STRUCT(b.name, b.operator, b.ref) 
	ORDER BY b.name) AS route 
	FROM ways_rh w JOIN buffer b 
	ON ST_ContainsProperly(b.geom,w.geom)
	WHERE b.route = 'bicycle' GROUP BY osm_id);
*/
ALTER TABLE ways_rh 
	ADD COLUMN route_name VARCHAR, 
	ADD COLUMN route_operator VARCHAR, 
	ADD COLUMN route_ref VARCHAR;

UPDATE ways_rh w SET route_name = r.name, route_operator = operator, route_ref = r.ref 
    FROM ways_rel r WHERE w.osm_id = r.osm_id;

DROP VIEW ways_rel;
DROP MATERIALIZED VIEW buffer;
