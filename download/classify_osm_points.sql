/*
Find points interesting for cycling or cycling planning
Update table names as needed
*/
/*
CREATE TABLE points_infra AS 
    SELECT * FROM pointskbh 
    WHERE barrier IS NOT NULL OR bollard IS NOT NULL OR (crossing IS NOT NULL AND crossing != 'no') OR "crossing:ref" IS NOT NULL 
    OR "crossing:island" IS NOT NULL OR highway IN ('crossing','traffic_signals') OR traffic_calming IS NOT NULL 
    OR traffic_sign IS NOT NULL OR traffic_signals IS NOT NULL;

CREATE TABLE points_service AS SELECT * FROM pointskbh 
WHERE amenity ILIKE '%bicycle%' OR "service:bicycle:chain_tool" IN ('yes','free') 
OR "service:bicycle:pump" IN ('yes','free') OR shop ILIKE '%bicycle%';
*/
UPDATE points_infra SET crossing = 'crossing' 
WHERE crossing IS NULL AND highway = 'crossing';

UPDATE points_infra SET traffic_signals = highway 
WHERE traffic_signals IS NULL AND highway = 'traffic_signals';