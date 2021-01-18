'''
This script converts linestrings into point geometries to be used for extracting elevation from a DEM
For lines longer than 20 meters (the resolution of the DEM) more point geometries are added at 20 meter intervals
'''
-- Table with all original point geometries and new points add 20 meter intervals
CREATE TABLE point_geometries AS
    SELECT osm_id, length_, (ST_DumpPoints(ST_Segmentize(geometry,20))).geom AS geom, 
        (ST_DumpPoints(ST_Segmentize(geometry,20))).path[2] as path
        FROM ways_rh
;

CREATE INDEX p_geom_idx
  ON point_geometries
  USING GIST (geom)
;

-- View to be used to get start and end points from the multilinestrings
CREATE VIEW linestrings AS
	(SELECT osm_id, ST_LineMerge(geometry) geom 
	FROM ways_rh)
;

-- Table with start and end points for all linestrings in ways
CREATE TEMPORARY TABLE start_point AS 
	SELECT osm_id, ST_StartPoint(geom) as geom
    FROM linestrings
;
ALTER TABLE start_point ADD COLUMN type VARCHAR DEFAULT 's';

CREATE TEMPORARY TABLE end_point AS 
	SELECT osm_id, ST_EndPoint(geom) as geom
    FROM linestrings
;

ALTER TABLE end_point ADD COLUMN type VARCHAR DEFAULT 'e';

CREATE TABLE start_end_points AS
	(SELECT * FROM start_point
	UNION
	SELECT * FROM end_point ORDER BY osm_id)
;

CREATE INDEX s_e_p_geom_idx
  ON start_end_points
  USING GIST (geom)
;

'''
-- If original points execpt start and end points should be removed 
-- (results in more than 20 meters between some points due to the functionality of ST_Segmentize)

-- Table with original point geometries
CREATE TEMPORARY TABLE org_points AS 
    SELECT osm_id, length_, (ST_DumpPoints(geometry)).path[2] as path,
    (ST_DumpPoints(geometry)).geom
    FROM ways_rh
;

CREATE INDEX org_p_geom_idx
  ON org_points
  USING GIST (geom)
;

-- Deleting start and end points from org points
DELETE FROM org_points o 
    WHERE EXISTS (SELECT FROM start_end_points s 
		WHERE o.osm_id = s.osm_id AND ST_EQUALS(o.geom, s.geom))
;

-- Deleting remaining org points from point geometries (ensure an even spacing of points along a line)
DELETE FROM point_geometries p 
    WHERE EXISTS (SELECT FROM org_points o 
		WHERE p.osm_id = o.osm_id AND ST_EQUALS(p.geom, o.geom))
;

DROP VIEW linestrings;
'''

-- Add column for elevation and ID for identifying individual nodes
ALTER TABLE point_geometries ADD COLUMN elevation FLOAT DEFAULT NULL;
ALTER TABLE point_geometries ADD COLUMN id SERIAL PRIMARY KEY;

-- Find elevation for each geometry - for detailed elevation profiles
CREATE VIEW point_elevation AS
    SELECT rid, ST_Value(rast, 1, p.geom) AS elevation, osm_id, path, id, ST_AsText(p.geom) geom
        FROM dhm_05_02, point_geometries p
            WHERE ST_Intersects(rast,p.geom) ORDER BY osm_id, path
;


'''
Plan: find elevation for all start and end points, calculate slope for each way
'''