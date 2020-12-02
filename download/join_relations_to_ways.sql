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

UPDATE wayskbh 
    ADD COLUMN route_name VARCHAR, 
    ADD COLUMN route_operator VARCHAR, 
    ADD COLUMN route_ref VARCHAR;

/*
Python dataframe?
Loop through ids.
For all ids i combine col values to list (for all three rel cols)