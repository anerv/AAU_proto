/*
This script contains the SQL statements classifying the OSM data
*/

-- OBS! Find a way to add table name to script


-- Finding segments for roads with car traffic
SELECT * from osmwayskbh WHERE "highway" ILIKE '%corridor%'   
OR "highway" ILIKE '%living_street%'   
OR "highway" ILIKE '%motorway%'    
OR "highway" ILIKE '%primary%'   
OR "highway" ILIKE '%residential%'   
OR "highway" ILIKE '%secondary%'     
OR "highway" ILIKE '%service%'   
OR "highway" ILIKE '%tertiary%'    
OR "highway" ILIKE '%trunk%'  
OR "highway" =  'unclassified' AND "name"IS NOT NULL AND "access" NOT IN  
('no', 'restricted');

-- OBS - then do what??


-- Finding segments with cycling infrastructure along a street
SELECT * from osmwayskbh WHERE 
-- OBS! Change - find roads with cars first, and then select from them???
"highway" ILIKE '%corridor%'   
OR "highway" ILIKE '%living_street%'   
OR "highway" ILIKE '%motorway%'     
OR "highway" ILIKE '%primary%'   
OR "highway" ILIKE '%residential%'   
OR "highway" ILIKE '%secondary%'      
OR "highway" ILIKE '%service%'   
OR "highway" ILIKE '%tertiary%'   
OR "highway" ILIKE '%trunk%'  
OR "highway" =  'unclassified' AND "name"IS NOT NULL AND "access" NOT IN  
('no', 'restricted') 
AND

"bicycle"  = 'designated'
OR "cycleway"  ILIKE '%separate%'
OR "cycleway" ILIKE '%designated%' 
OR "cycleway" ILIKE '%crossing%'
OR "cycleway" ILIKE '%lane%' 
OR "cycleway" ILIKE '%opposite%' 
OR "cycleway" ILIKE '%track%' 
OR "cycleway" ILIKE '%yes%'
OR "cycleway:left" ILIKE '%lane%'
OR "cycleway:left" ILIKE '%opposite%'
OR "cycleway:left" ILIKE '%track%'
OR "cycleway:right" ILIKE '%lane%'
OR "cycleway:right" ILIKE '%opposite%'
OR "cycleway:right" ILIKE '%track%'
OR "cycleway:both" ILIKE '%lane%'
OR "cycleway:both" ILIKE '%opposite%'
OR "cycleway:both" ILIKE '%track%';

-- OBS - then do what??

-- Select segments where cyclists are sharing a lane with other modes of traffic
SELECT * FROM osmwayskbh WHERE 
"cycleway" ILIKE '%shared_lane%'
OR "bicycle" ILIKE '%shared_lane%'
OR "cycleway:left" ILIKE '%shared_lane%' 
OR "cycleway:right" ILIKE '%shared_lane%'
OR "cycleway:both" ILIKE '%shared_lane%';

-- OBS - then do what??

-- Finding segments where cycling against the flow of traffic is allowed
SELECT * FROM osmwayskbh 
WHERE "Cycleway" ILIKE '%opposite%'
OR "oneway:bicycle" = 'no' 
AND "oneway" IN ('yes', 'true');

-- OBS - then do what??

-- Finding segments with cycling infrastructure away from car streets
SELECT * FROM osmwayskbh WHERE....

-- 