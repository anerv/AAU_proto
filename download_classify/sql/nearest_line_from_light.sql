/*
The query finds the nearest line from a point representing a street light
*/

-- Create view of street lights joined to the nearest way
CREATE VIEW lights_ways AS (SELECT DISTINCT ON (p."LUM_ID")
    p."LUM_ID" AS point, w.name AS closest_way, w.osm_id, w.lit, ST_Distance(p.geom,w.geom) AS dist 
    FROM street_light AS p
    LEFT JOIN ways_rh AS W ON ST_DWithin(p.geom,w.geom,5)
    ORDER BY p."LUM_ID", dist);

-- Update way based on view
UPDATE ways_rh w SET lit = 'yes' FROM lights_ways l 
    WHERE w.osm_id = l.osm_id;

DROP VIEW lights_ways;

