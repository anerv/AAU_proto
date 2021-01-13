--This scripts adds data about which adminstrative unit a features is in
-- Change table and column names as needed


ALTER TABLE ways_rh ADD COLUMN adm VARCHAR DEFAULT NULL;
ALTER TABLE points_infra ADD COLUMN adm VARCHAR DEFAULT NULL;
ALTER TABLE points_service ADD COLUMN adm VARCHAR DEFAULT NULL;
ALTER TABLE poly_service ADD COLUMN adm VARCHAR DEFAULT NULL;

-- Adding data to ways

/*
-- First method - only one adm unit per way
-- For ways the centroid is used to ensure that a segment only is assigned to one municipality
CREATE MATERIALIZED VIEW ways_adm_cent AS
    SELECT w.osm_id, s.navn AS adm FROM ways_rh w 
    JOIN study_area_rh s ON ST_Contains(s. geometry, ST_Centroid(w.geometry)) GROUP BY osm_id;

-- The a view solely based on intersects are used for those where the centroid is outside of the polygon layer
CREATE MATERIALIZED VIEW ways_adm AS
    SELECT w.osm_id, s.navn AS adm FROM ways_rh w 
    JOIN study_area_rh s ON ST_Intersects(s. geometry, w.geometry)
    WHERE w.adm IS NULL;


CREATE INDEX osmid2 ON ways_adm_cent (osm_id);
CREATE INDEX osmid3 ON ways_adm (osm_id);


UPDATE ways_rh w SET adm = a.adm 
    FROM ways_adm_cent a WHERE w.osm_id = a.osm_id;

UPDATE ways_rh w SET w.adm = a.adm 
    FROM ways_adm a WHERE w.osm_id = a.osm_id
    AND w.adm IS NULL;

*/

-- Second method, if all adm areas intersecting segment are wanted

CREATE MATERIALIZED VIEW ways_adm_all AS 
	SELECT w.osm_id, string_agg(DISTINCT s.navn, ', ') AS adm FROM ways_rh w 
    JOIN study_area_rh s ON ST_Intersects(w.geometry, s.geometry) GROUP BY osm_id;

--CREATE INDEX osmid4 ON ways_adm_all(osm_id);

UPDATE ways_rh w SET adm = a.adm 
    FROM ways_adm_all a WHERE w.osm_id = a.osm_id;


UPDATE points_infra p SET adm = s.navn FROM study_area_rh s 
    WHERE ST_Intersects(p.geometry, s.geometry);

UPDATE points_service p SET adm = s.navn FROM study_area_rh s 
    WHERE ST_Intersects(p.geometry, s.geometry);

UPDATE poly_service p SET adm = s.navn FROM study_area_rh s 
    WHERE ST_Contains(s.geometry, ST_Centroid(p.geometry));

