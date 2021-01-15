
-- Line features must be converted to centroids to be queried as lat long
ALTER TABLE ways_rh 
    ADD COLUMN lat FLOAT, 
    ADD COLUMN long FLOAT;

UPDATE ways_rh 
    SET long = ST_X (ST_Transform(ST_Centroid(geom),4326)),
    lat = ST_Y(ST_Transform(ST_Centroid(geom),4326));

-- Traffic counts
ALTER TABLE traffic_counts 
    ADD COLUMN lat FLOAT, 
    ADD COLUMN long FLOAT;

UPDATE traffic_counts 
    SET long = ST_X (ST_Transform(geom,4326)),
    lat = ST_Y(ST_Transform(geom,4326));

-- Bicycle service polygons
ALTER TABLE poly_service
    ADD COLUMN lat FLOAT, 
    ADD COLUMN long FLOAT;

UPDATE poly_service 
    SET long = ST_X (ST_Transform(ST_Centroid(geom),4326)),
    lat = ST_Y(ST_Transform(ST_Centroid(geom),4326));

-- Bicycle infrastructure
ALTER TABLE points_infra
    ADD COLUMN lat FLOAT,
    ADD COLUMN long FLOAT;

UPDATE points_infra 
    SET long = ST_X (ST_Transform(geom,4326)),
    lat = ST_Y(ST_Transform(geom,4326));

-- Bicycle service
ALTER TABLE points_service
    ADD COLUMN lat FLOAT,
    ADD COLUMN long FLOAT;

UPDATE points_service 
    SET long = ST_X (ST_Transform(geom,4326)),
    lat = ST_Y(ST_Transform(geom,4326));