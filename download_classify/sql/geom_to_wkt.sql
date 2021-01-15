-- Script transforms geometryetry object type to well known text and lat long (EPSG:4326)
-- (useful for importing data into e.g. Power BI)

ALTER TABLE ways_rh ADD COLUMN wkt VARCHAR;
UPDATE ways_rh SET wkt = St_AsText(ST_Transform(geometry,4326));

ALTER TABLE traffic_counts ADD COLUMN wkt VARCHAR;
UPDATE traffic_counts SET wkt = St_AsText(ST_Transform(geometry,4326));

ALTER TABLE points_infra ADD COLUMN wkt VARCHAR;
UPDATE points_infra SET wkt = St_AsText(ST_Transform(geometry,4326));

ALTER TABLE points_service ADD COLUMN wkt VARCHAR;
UPDATE points_service SET wkt = St_AsText(ST_Transform(geometry,4326));

ALTER TABLE poly_service ADD COLUMN wkt VARCHAR;
UPDATE poly_service SET wkt = St_AsText(ST_Transform(geometry,4326));


