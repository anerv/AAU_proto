-- Script transforms geometry object type to well known text 
-- (useful for importing data into e.g. Power BI)

ALTER TABLE ways_rh ADD COLUMN wkt VARCHAR;
UPDATE ways_rh SET wkt = St_AsText(ST_Transform(geom,4326));

ALTER TABLE traffic_counts ADD COLUMN wkt VARCHAR;
UPDATE traffic_counts SET wkt = St_AsText(ST_Transform(geom,4326));

ALTER TABLE points_infra ADD COLUMN wkt VARCHAR;
UPDATE points_infra SET wkt = St_AsText(ST_Transform(geom,4326));

ALTER TABLE points_service ADD COLUMN wkt VARCHAR;
UPDATE points_service SET wkt = St_AsText(ST_Transform(geom,4326));

ALTER TABLE poly_service ADD COLUMN wkt VARCHAR;
UPDATE poly_service SET wkt = St_AsText(ST_Transform(geom,4326));

ALTER TABLE noise_variables ADD COLUMN wkt VARCHAR;
UPDATE noise_variables SET WKT = ST_AsText(ST_Transform(geom,4326));


-- If data will be used in PowerBi with icon map, a size column is needed. 
-- In this case the value is irrelevant, but should be consistent

ALTER TABLE ways_rh ADD COLUMN size INTEGER;
UPDATE ways_rh SET size = 1;

ALTER TABLE traffic_counts ADD COLUMN size INTEGER;
UPDATE traffic_counts SET size = 1;

ALTER TABLE points_infra ADD COLUMN size INTEGER;
UPDATE points_infra SET size = 1;

ALTER TABLE points_service ADD COLUMN size INTEGER;
UPDATE points_service SET size = 1;

ALTER TABLE poly_service ADD COLUMN size INTEGER;
UPDATE poly_service SET size = 1;

ALTER TABLE noise_variables ADD COLUMN size INTEGER;
UPDATE noise_variables SET size = 1;
