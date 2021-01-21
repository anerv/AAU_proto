/*
This scripts adds the id of the closest way with car traffic to enable joins based on id
*/

ALTER TABLE noise_variables
    ADD COLUMN id SERIAL PRIMARY KEY,
    ADD COLUMN osm_id INTEGER
;

ALTER TABLE noise_variables ADD
    CONSTRAINT ways_id
        FOREIGN KEY(osm_id) 
        REFERENCES ways_rh(osm_id)
;

UPDATE noise_variables n
SET osm_id = (
  SELECT w.osm_id
  FROM ways_rh w
  ORDER BY n.geom <-> w.geom
  LIMIT 1
);
