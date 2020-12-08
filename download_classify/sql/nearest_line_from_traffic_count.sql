/*
The query finds the nearest line from a point representing a traffic count and update line attributes based on the nearest point
*/

ALTER TABLE traffic_counts 
ADD COLUMN id SERIAL PRIMARY KEY;

ALTER TABLE waysdk
ADD COLUMN car_aadt INTEGER,
ADD COLUMN bike_aadt INTEGER;

-- Create view of traffic counts joined to the nearest way
CREATE VIEW counts_car AS (SELECT DISTINCT ON (t.id)
    t.id AS point, t.geometry, t."AADT", w.name AS closest_way, w.osm_id, ST_Distance(t.geometry,w.geometry) AS dist 
    FROM traffic_counts AS t
    LEFT JOIN waysdk AS w ON ST_DWithin(t.geometry,w.geometry,10) 
	WHERE w.car_traffic = 'yes' AND t."KOERETOEJS" = 'MOTORKTJ'
    ORDER BY t.id, dist);

CREATE VIEW counts_bike AS (SELECT DISTINCT ON (t.id)
    t.id AS point, t.geometry, t."AADT", w.name AS closest_way, w.osm_id, ST_Distance(t.geometry,w.geometry) AS dist 
    FROM traffic_counts AS t
    LEFT JOIN waysdk AS w ON ST_DWithin(t.geometry,w.geometry,10) 
	WHERE w.cycling_infrastructure IS NOT NULL AND t."KOERETOEJS" IN('CYKLER','C/K')
    ORDER BY t.id, dist);

CREATE VIEW counts_bike_road AS (SELECT DISTINCT ON (t.id)
    t.id AS point, t.geometry, t."AADT", w.name AS closest_way, w.osm_id, ST_Distance(t.geometry,w.geometry) AS dist 
    FROM traffic_counts AS t
    LEFT JOIN waysdk AS w ON ST_DWithin(t.geometry,w.geometry,10) 
	WHERE t."KOERETOEJS" IN('CYKLER','C/K')
    ORDER BY t.id, dist);
    
-- Update way based on view
UPDATE waysdk w SET car_aadt = "AADT" FROM counts_car c
    WHERE w.osm_id = c.osm_id;

-- Cycling counts added to cycling infrastructure
UPDATE waysdk w SET bike_aadt = "AADT" FROM counts_bike c
    WHERE w.osm_id = c.osm_id;

-- Cycling counts added to nearest way regardless of type
UPDATE waysdk w SET bike_aadt = "AADT" FROM counts_bike_road c
    WHERE w.osm_id = c.osm_id;


-- This table also contains data about average speed and speed limit
CREATE VIEW speed AS (SELECT DISTINCT ON (t.id)
    t.id AS point, t.geometry, t."GNS_HASTIG", t."HAST_GRAEN", w.name AS closest_way, w.osm_id, ST_Distance(t.geometry,w.geometry) AS dist 
    FROM traffic_counts AS t
    LEFT JOIN waysdk AS w ON ST_DWithin(t.geometry,w.geometry,10)
    WHERE w.car_traffic = 'yes' AND  t."KOERETOEJS" = 'MOTORKTJ'
    ORDER BY t.id, dist);

ALTER TABLE waysdk ADD COLUMN ave_speed NUMERIC;

UPDATE waysdk w SET maxspeed = "HAST_GRAEN" FROM speed s
    WHERE w.osm_id = s.osm_id AND maxspeed IS NULL;

UPDATE waysdk w SET ave_speed = "GNS_HASTIG" FROM speed s 
    WHERE w.osm_id = s.osm_id;


DROP VIEW counts_car;
DROP VIEW counts_bike;
DROP VIEW counts_bike_road;
DROP VIEW speed;
