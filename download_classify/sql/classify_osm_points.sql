/*
Find points interesting for cycling or cycling planning
Update table names as needed
*/

CREATE TABLE points_infra AS 
    SELECT * FROM points_rh 
    WHERE barrier IS NOT NULL OR bollard IS NOT NULL OR (crossing IS NOT NULL AND crossing != 'no') 
    OR "crossing:island" IS NOT NULL OR highway IN ('crossing','traffic_signals') OR traffic_calming IS NOT NULL 
    OR traffic_sign IS NOT NULL OR traffic_signals IS NOT NULL;

CREATE TABLE points_service AS SELECT * FROM points_rh 
WHERE amenity ILIKE '%bicycle%' OR "service:bicycle:chain_tool" IN ('yes','free') 
OR "service:bicycle:pump" IN ('yes','free') OR shop ILIKE '%bicycle%';

UPDATE points_infra SET crossing = 'crossing' 
WHERE crossing IS NULL AND highway = 'crossing';

UPDATE points_infra SET traffic_signals = highway 
WHERE traffic_signals IS NULL AND highway = 'traffic_signals';

ALTER TABLE points_infra DROP COLUMN amenity, DROP COLUMN area, DROP COLUMN flashing_lights, DROP COLUMN parking,
    DROP COLUMN public_transport, DROP COLUMN railway, DROP COLUMN ref, DROP COLUMN service, DROP COLUMN "service:bicycle:chain_tool", 
    DROP COLUMN "service:bicycle:pump", DROP COLUMN shop;

ALTER TABLE points_service DROP COLUMN area, DROP COLUMN barrier, DROP COLUMN bicycle, DROP COLUMN bollard, DROP COLUMN crossing, 
    DROP COLUMN "crossing:island", DROP COLUMN "crossing:ref", DROP COLUMN ele, DROP COLUMN flashing_lights, 
    DROP COLUMN foot, DROP COLUMN highway, DROP COLUMN parking, DROP COLUMN public_transport, DROP COLUMN railway,
    DROP COLUMN ref, DROP COLUMN segregated, DROP COLUMN surface, DROP COLUMN traffic_calming, DROP COLUMN traffic_sign,
    DROP COLUMN traffic_signals;
