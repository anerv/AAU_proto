/*
This script updates the attribute for ways data based on the land cover
*/

ALTER TABLE ways_rh 
ADD COLUMN landscape VARCHAR, 
ADD COLUMN close_to VARCHAR;

CREATE MATERIALIZED VIEW ways_lc AS 
	SELECT w.osm_id, string_agg(DISTINCT l.label_modified, ', ') AS landcover FROM ways_rh w 
    JOIN lc_sa l ON ST_Intersects(w.geom, l.geom) GROUP BY osm_id;

CREATE INDEX osmid ON ways_lc (osm_id);

UPDATE ways_rh w SET landscape = landcover
    FROM ways_lc lc WHERE w.osm_id = lc.osm_id;

-- Handling ways outside of land use polygons
-- Creating and updating views can be repeated a number of times to decrease number of ways with no lanscape info
CREATE VIEW unknown_lu AS (SELECT osm_id, landscape, geom FROM ways_rh WHERE landscape IS NULL);
CREATE VIEW known_lu AS (SELECT osm_id, landscape, geom FROM ways_rh WHERE landscape IS NOT NULL);
UPDATE unknown_lu ul SET landscape = kl.landscape FROM known_lu kl 
	WHERE ST_Touches(ul.geom, kl.geom);

DROP VIEW unknown_lu;
DROP VIEW known_lu;

-- Dissolve adjacent land cover polygons with same type of land use
CREATE TABLE land_cover_simple AS SELECT (ST_DUMP(ST_UNION(geom))).geom, label_modified FROM lc_sa GROUP BY label_modified;

-- Determing which type of landscape a way is close to
CREATE MATERIALIZED VIEW close_to AS
	SELECT w.osm_id, string_agg(DISTINCT l.label_modified, ', ') AS landcover FROM ways_rh w, land_cover_simple l
	WHERE ST_DWithin(w.geom, l.geom, 20) AND NOT ST_Intersects(w.geom, l.geom)
	GROUP BY osm_id;

CREATE INDEX osmid_c ON ways_close_to (osm_id);

UPDATE ways_rh w SET close_to = landcover 
	FROM close_to c WHERE w.osm_id = c.osm_id;

-- Update based on coastline
UPDATE ways_rh w SET landscape = 'coast'
	FROM coastline c WHERE ST_DWithin(w.geom, c.geom, 50) 
	AND landscape IS NULL;

UPDATE ways_rh w SET close_to = CONCAT(close_to, ', coastline')
	FROM coastline c WHERE ST_DWithin(w.geom, c.geom, 50) 
	AND close_to IS NOT NULL;

UPDATE ways_rh w SET close_to = 'coastline'
	FROM coastline c WHERE ST_DWithin(w.geom, c.geom, 50) 
	AND close_to IS NULL;

UPDATE ways_rh w SET landscape = 'coast'
	FROM land_use_rh l WHERE l.natural = 'coastline' 
	AND ST_DWithin(w.geom, l.geom, 50) AND landscape IS NULL;

-- Try to fix remaining unknown landscape
CREATE VIEW unknown_lu AS (SELECT osm_id, landscape, geom FROM ways_rh WHERE landscape IS NULL);
CREATE VIEW known_lu AS (SELECT osm_id, landscape, geom FROM ways_rh WHERE landscape IS NOT NULL);
UPDATE unknown_lu ul SET landscape = kl.landscape FROM known_lu kl 
	WHERE ST_Touches(ul.geom, kl.geom);

DROP VIEW unknown_lu;
DROP VIEW known_lu;

--DROP VIEW ways_lc;
--DROP VIEW ways_close_to;
