/* Script for computing a more detailed elevation profile for a route/path of linestrings/ways 
The method requires the unique identifier/primary key, and they must be provided in the correct order, 
corresponding to the sequence of the ways 
If IDS are provided in the wrong order the order can be restored by sorting by first path ASC and then x or y, DESC
The code has been tested on ways which form a more or less straight line - if the line is circular or winding sorting by coordinate will not work!  */


CREATE TABLE route AS (SELECT ST_Union(
	ARRAY(SELECT geometry FROM ways_rh WHERE osm_id IN (70365184, 783687962, 70365182)) 
) AS geom);

CREATE TABLE points AS
    SELECT (ST_Dumppoints(ST_Segmentize(geom,2))).geom AS geom, 
        (ST_Dumppoints(ST_Segmentize(geom,2))).path[2] as path
        FROM route
;

ALTER TABLE points ADD COLUMN id SERIAL PRIMARY KEY;

ALTER TABLE points 
    ADD COLUMN x_coord FLOAT,
    ADD COLUMN y_coord FLOAT,
    ADD COLUMN z_coord FLOAT
;

UPDATE points SET 
    x_coord = ST_X(geom),
    y_coord = ST_Y(geom)
;

UPDATE points p SET z_coord = ST_NearestValue(rast, 1, p.geom) 
  FROM dhm_tiled d WHERE ST_Intersects(d.rast, p.geom)
;

-- Removing duplicate geometries (occur where adjacent lines meet)
-- Removes the point with the largest id
DELETE FROM points p1
 WHERE EXISTS (SELECT FROM points p2
                WHERE p1.id > p2.id
                  AND ST_EQUALS(p1.geom, p2.geom)
);

/*
751162442
751162441
496720678


70365184
70365182
783687962
*/