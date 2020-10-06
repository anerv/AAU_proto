/*
This script contains the SQL statements classifying the OSM data
*/

-- OBS! Find a way to add table name to script
-- Rewrite to python functions taking table name as input?

-- Creating new columns
ALTER TABLE osmwayskbh 
ADD COLUMN car_traffic VARCHAR DEFAULT NULL, --OK
ADD COLUMN road_type VARCHAR DEFAULT NULL,
ADD COLUMN cycling_infrastructure VARCHAR DEFAULT NULL,
ADD COLUMN cycling_friendly VARCHAR DEFAULT NULL,
ADD COLUMN cycling_possible VARCHAR DEFAULT NULL, -- ADD MORE
ADD COLUMN cycling_against VARCHAR DEFAULT NULL, -- OK
ADD COLUMN elevation NUMERIC DEFAULT NULL,
ADD COLUMN pedestrian VARCHAR DEFAULT NULL, --OK
ADD COLUMN on_street_park VARCHAR DEFAULT NULL; --OK


-- Updating value in column car_traffic
UPDATE osmwayskbh SET car_traffic = 'yes' 
WHERE "highway" ILIKE '%corridor%'   
OR "highway" ILIKE '%living_street%'   
OR "highway" ILIKE '%motorway%'    
OR "highway" ILIKE '%primary%'   
OR "highway" ILIKE '%residential%'   
OR "highway" ILIKE '%secondary%'     
OR "highway" ILIKE '%service%'   
OR "highway" ILIKE '%tertiary%'    
OR "highway" ILIKE '%trunk%'  
OR "highway" =  'unclassified' AND "name" IS NOT NULL AND "access" NOT IN  
('no', 'restricted');

/*Determining overall road type. The assignment of road type is based on a hierarchy 
where the road type which usually has the highest speed and most traffic determines the type
*/
UPDATE osmwayskbh SET road_type =
    (CASE WHEN "highway" ILIKE 'motorway' THEN 'motorvej'
        WHEN "highway" ILIKE ''
        WHEN "highway" ILIKE ''
        WHEN "highway" = 'elevator' THEN 'not_road'
        ELSE 'unknown');

-- begin lowest in hieararchy?


-- Finding all segments with cycling infrastructure
UPDATE osmwayskbh SET cycling_infrastructure = 'cykelinfrastruktur'
WHERE "bicycle"  = 'designated'
OR "highway" = -- something HERE!!! Find cycleways, which to include?

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

-- Finding segments with cycling infrastructure along a street
UPDATE osmwayskbh SET cycling_infrastructure = 'cykelinfrastruktur langs vej'
WHERE car_traffic = 'yes'
(AND "bicycle"  = 'designated'
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
OR "cycleway:both" ILIKE '%track%');

-- Segments with cycling infrastructure away from car streets (cykling i eget trace)
/*
The query below selects highway = cycleway which do not run along a street with car traffic
*/
SELECT * FROM osmwayskbh WHERE....


-- Segments where cyclists are sharing a lane with other modes of traffic
UPDATE TABLE osmwayskbh SET cycling_infrastructure = 'shared_lane' 
WHERE "cycleway" ILIKE '%shared_lane%'
OR "bicycle" ILIKE '%shared_lane%'
OR "cycleway:left" ILIKE '%shared_lane%' 
OR "cycleway:right" ILIKE '%shared_lane%'
OR "cycleway:both" ILIKE '%shared_lane%';


-- Segments where cycling against the flow of traffic is allowed
UPDATE TABLE osmwayskbh SET cycling_against = 'yes'
WHERE "Cycleway" ILIKE '%opposite%'
OR "oneway:bicycle" = 'no' 
AND "oneway" IN ('yes', 'true');

-- Segments where cycling is specified as allowed or assumed allowed based on other attributes (mostly interesting for non-cycling infrastructure)
UPDATE TABLE osmwayskbh SET cycling_possible = 'yes' 
WHERE "bicycle" IN ('permissive', 'ok', 'allowed')
OR "highway" ILIKE '%cycleway%'
OR -- add more here - which road types allways allow for cycling?;

-- Segments where pedestrians are allowed
UPDATE TABLE osmwayskbh SET pedestrian = 'yes' 
WHERE "highway" ILIKE '%pedestrian%' 
OR "highway" ILIKE '%path%'
OR "highway" ILIKEfootway '%steps%'
OR "foot" ILIKE '%yes%'
OR "foot" ILIKE '%designated%' 
OR "foot" ILIKE'%permissive%' 
OR "foot" ILIKE '%official%'
OR "sidewalk" ILIKE '%both%' 
OR "sidewalk" ILIKE '%left%'
OR "sidewalk" ILIKE '%right%'
OR "sidewalk" ILIKE '%separate%';


-- Segments with on street parking
UPDATE TABLE osmwayskbh SET on_street_park = 'yes' 
WHERE "parking:lane:both" ILIKE '%diagonal%'
OR "parking:lane:both" ILIKE '%parallel%'
OR "parking:lane:both" ILIKE '%perpendicilar%'
OR "parking:lane:left" ILIKE '%diagonal%'
OR "parking:lane:left" ILIKE '%parallel%'
OR "parking:lane:left" ILIKE '%perpendicular%'
OR "parking:lane:right" ILIKE '%diagonal%'
OR "parking:lane:right" ILIKE '%parallel%'
OR "parking:lane:right" ILIKE '%perpendicular%'
OR "parking:lane" ILIKE '%diagonal%'
OR "parking:lane" ILIKE '%parallel%'
OR "parking:lane" ILIKE '%perpendicular%';

-- Cycling friendly segments
/*
Should both be based on elevation, surface, speed, number of lanes, presence of cycling infrastructure
cycle friendly paths etc
*/

-- Finally, dealing with unclassified segments