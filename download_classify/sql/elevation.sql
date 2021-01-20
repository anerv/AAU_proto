'''
This script converts linestrings into point geometries to be used for extracting elevation from a DEM
Different methods are used: One for finding elevation of all start and end points for ways, which can be used to compute slope.
Another one which segment all lines longer than 20 meter into smaller segments and adds elevation to all points (gives a more detailed elevation profile)
Neither of the methods can handle locations with several layers of roads (e.g. bridge over a highway), and the first method has some drawbacks with very long way segments (loss of detail)
For lines longer than 20 meters more point geometries are added at 20 meter intervals
The performance for computing slope and aspect rasters with PostGIS appears to be quite poor - it is recommended to use Python with GDAL or rasterio instead
'''
-- Important! Using tiles of 100*100 speeds up performance a lot

-- Create a new table for tiled raster
CREATE TABLE dhm_tiled(
  rid SERIAL primary key, rast raster
);
-- Tile raster
INSERT INTO dhm_tiled(rast)
  SELECT ST_Tile(rast, 1, 100, 100, TRUE, 0)
  FROM dhm_05
;

-- Table with all original point geometries and new points add 20 meter intervals
CREATE TABLE point_geometries AS
    SELECT osm_id, length_, (ST_DumpPoints(ST_Segmentize(geometry,20))).geom AS geom, 
        (ST_DumpPoints(ST_Segmentize(geometry,20))).path[2] as path
        FROM ways_rh
;

ALTER TABLE point_geometries
    ADD CONSTRAINT fk_ways FOREIGN KEY (osm_id) REFERENCES ways_rh (osm_id)
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
CREATE TABLE start_points AS 
	SELECT osm_id, ST_StartPoint(geom) as geom
    FROM linestrings
;
ALTER TABLE start_points 
  ADD COLUMN type VARCHAR DEFAULT 's',
  ADD COLUMN elevation FLOAT DEFAULT NULL;

CREATE TABLE end_points AS 
	SELECT osm_id, ST_EndPoint(geom) as geom
    FROM linestrings
;

ALTER TABLE end_points 
  ADD COLUMN type VARCHAR DEFAULT 'e',
  ADD COLUMN elevation FLOAT DEFAULT NULL
;

-- SET SRID
ALTER TABLE start_points
  ALTER COLUMN geom TYPE geometry(POINT, 25832)
    USING ST_SetSRID(geom, 25832)
;

ALTER TABLE end_points
  ALTER COLUMN geom TYPE geometry(POINT, 25832)
    USING ST_SetSRID(geom, 25832)
;

CREATE INDEX s_geom_idx
  ON start_points
  USING GIST (geom)
;

CREATE INDEX e_geom_idx
  ON end_points
  USING GIST (geom)
;


-- Find elevation of start and end points
UPDATE start_points s SET elevation = ST_Value(rast, 1, s.geom) 
  FROM dhm_tiled d WHERE ST_Intersects(d.rast, s.geom)
;

UPDATE end_points e SET elevation = ST_Value(rast, 1, e.geom) 
  FROM dhm_tiled d WHERE ST_Intersects(d.rast, e.geom)
;

UPDATE end_points e SET elevation = ST_NearestValue(rast, 1, e.geom) 
  FROM dhm_tiled d WHERE ST_Intersects(d.rast, e.geom)
  AND elevation IS NULL
;

UPDATE start_points s SET elevation = ST_NearestValue(rast, 1, s.geom) 
  FROM dhm_tiled d WHERE ST_Intersects(d.rast, s.geom)
  AND elevation IS NULL
;

-- Using a tiled raster can cause issues for a small number of points
-- Use regular raster to update elevation for remaining
UPDATE start_points s SET elevation = ST_Value(rast, 1, s.geom) 
  FROM dhm_05 d WHERE ST_Intersects(d.rast, s.geom)
  AND elevation IS NULL
;

UPDATE end_points e SET elevation = ST_Value(rast, 1, e.geom) 
  FROM dhm_05 d WHERE ST_Intersects(d.rast, e.geom)
  AND elevation IS NULL
;

'''
CREATE TABLE start_end_points AS
	(SELECT * FROM start_point
	UNION
	SELECT * FROM end_point ORDER BY osm_id)
;
'''
CREATE TABLE start_end_points AS
  (SELECT s.osm_id, s.geom geom_s, e.geom geom_e, s.type type1, e.type type2, 
  s.elevation start_elevation, e.elevation end_elevation
  FROM start_points s JOIN end_points e ON s.osm_id = e.osm_id)
;

ALTER TABLE start_end_points
    ADD CONSTRAINT fk_ways FOREIGN KEY (osm_id) REFERENCES ways_rh (osm_id)
;

-- Computing slope for all ways based on start and end points
-- First all rows with null values for start/end geometries must be removed 
-- (can occur when data are clipped to extent of study area)
DELETE FROM start_end_points WHERE geom_s IS NULL OR geom_e IS NULL;
-- Removing lines where start and end point are the same
--DELETE FROM start_end_points WHERE geom_s = geom_e;

ALTER TABLE start_end_points 
  ADD COLUMN slope FLOAT DEFAULT NULL,
  ADD COLUMN ele_diff FLOAT DEFAULT NULL,
  ADD COLUMN length_ FLOAT DEFAULT NULL,
  ADD COLUMN slope_percent FLOAT DEFAULT NULL
;

UPDATE start_end_points s SET length_ = w.length_ 
  FROM ways_rh w WHERE s.osm_id = w.osm_id
;
UPDATE start_end_points SET ele_diff = end_elevation - start_elevation;
UPDATE start_end_points SET slope = ele_diff/length_;
UPDATE start_end_points SET slope_percent = slope * 100;

'''
-- If original points execpt start and end points should be removed from point geometries
-- (results in more than 20 meters between some points due to the functionality of ST_Segmentize)
-- Ideally, find a different method for even segmentation

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
'''
-- Creating slope table
CREATE TABLE slope_05 AS SELECT ST_Slope(d.rast, 1, '32BF', 'PERCENT', 1.0) AS slope, rast 
  FROM dhm_tiled d
;

ALTER TABLE slope_05 ADD COLUMN rid SERIAL PRIMARY KEY;
CREATE INDEX slope_gix ON slope_05 USING GIST(ST_Convexhull(rast));

-- Creating aspect table
CREATE TABLE aspect_05 AS SELECT ST_Aspect(d.rast, 1, '32BF') AS aspect, rast
  FROM dhm_05 d
;
ALTER TABLE aspect_05 ADD COLUMN rid SERIAL PRIMARY KEY;
CREATE INDEX aspect_gix ON aspect_05 USING GIST(ST_Convexhull(rast));

-- Add column for elevation and ID for identifying individual nodes
ALTER TABLE point_geometries ADD COLUMN id SERIAL PRIMARY KEY;
ALTER TABLE point_geometries ADD COLUMN elevation FLOAT DEFAULT NULL;
ALTER TABLE point_geometries ADD COLUMN slope FLOAT DEFAULT NULL;
ALTER TABLE point_geometries ADD COLUMN aspect FLOAT DEFAULT NULL;

-- Find slope and aspect for all point geometries
UPDATE point_geometries p SET slope = ST_Value(rast, 1, p.geom)
  FROM slope_05 s WHERE ST_Intersects(s.rast, p.geom)
;

UPDATE point_geometries p SET aspect = ST_Value(rast, 1, p.geom)
  FROM aspect_05 a WHERE ST_Intersects(a.rast, p.geom)
;

-- Find elevation for each point geometry - for detailed elevation profiles
UPDATE point_geometries p SET elevation = ST_Value(rast, 1, p.geom) 
  FROM dhm_tiled d WHERE ST_Intersects(d.rast, p.geom)
;

ALTER TABLE ways_rh ADD COLUMN slope_percent FLOAT DEFAULT NULL;

UPDATE ways_rh w SET slope_percent = s.slope_percent FROM start_end_points s
  WHERE w.osm_id = s.osm_id
;
'''
UPDATE point_geometries p SET elevation = ST_Value(rast, 1, p.geom) 
  FROM dhm_tiled d WHERE ST_Intersects(d.rast, p.geom)
;
UPDATE point_geometries p SET elevation = ST_NearestValue(rast, 1, p.geom) 
  FROM dhm_tiled d WHERE ST_Intersects(d.rast, p.geom)
;

'''
CREATE VIEW point_elevation AS
    SELECT rid, ST_Value(rast, 1, p.geom) AS elevation, osm_id, path, id, ST_AsText(p.geom) geom
        FROM dhm_05, point_geometries p
            WHERE ST_Intersects(rast,p.geom) ORDER BY osm_id, path
;
'''


WITH union_ AS (SELECT ST_Union(
	ARRAY(SELECT geometry FROM ways_rh WHERE route_ref ILIKE '%havnering%') 
) AS geom) SELECT St_segmentize(geom, 20) from union_;

CREATE TABLE testing AS (SELECT ST_Union(
	ARRAY(SELECT geometry FROM ways_rh WHERE route_ref ILIKE '%havnering%') 
) AS geom);

CREATE TABLE testing2 AS (SELECT ST_Union(
	ARRAY(SELECT geometry FROM ways_rh WHERE osm_id IN (496720678, 751162441, 751162442)) 
) AS geom);


SELECT ST_Segmentize(geom, 200) FROM testing;

CREATE TABLE test_points AS
    SELECT (ST_DumpPoints(ST_Segmentize(geom,20))).geom AS geom, 
        (ST_DumpPoints(ST_Segmentize(geom,20))).path[2] as path
        FROM testing
;
