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


/*Determining overall road type. The assignment of road type is based on a hierarchy 
where the road type which usually has the highest speed and most traffic determines the type
*/
UPDATE osmwayskbh SET road_type =
    (CASE
        WHEN highway ILIKE '%motorway%' THEN 'motorvej'
        WHEN highway ILIKE '%trunk%' THEN 'motortrafikvej'
        WHEN highway ILIKE '%primary%' THEN 'primærrute'
        WHEN highway ILIKE '%secondary%' THEN 'sekundærrute/ringvej'
        WHEN highway ILIKE '%tertiary%' THEN 'større vej'
        WHEN highway ILIKE '%residential%' THEN 'beboelsesvej'
        WHEN highway ILIKE '%service%' THEN 'adgangsvej/parkering/privatvej_osv'
        WHEN highway ILIKE '%living_street' THEN 'begrænset biltrafik'
        WHEN highway ILIKE '%pedestrian%' THEN 'gågade_gangområde'
        WHEN highway ILIKE '%path%' THEN 'sti'
        WHEN highway ILIKE '%cycleway%' THEN 'cykelsti'
        WHEN highway ILIKE '%cycleway%' AND highway ILIKE 'footway' THEN 'cykel- og gangsti'
        WHEN highway ILIKE '%footway%' THEN 'gangsti'
        WHEN highway ILIKE '%track%' THEN 'sti'
        WHEN highway ILIKE '%steps%' THEN 'trappe'
        WHEN highway = 'elevator' OR highway = 'corridor' THEN 'ikke_vej'
        ELSE 'ukendt'
        END);

 -- Limiting number of road segments with road type 'unknown'
CREATE VIEW unknown_roadtype AS (SELECT name, osmid, highway, road_type, geometry FROM osmwayskbh WHERE road_type = 'ukendt');
CREATE VIEW known_roadtype AS (SELECT name, osmid, highway, road_type, geometry FROM osmwayskbh WHERE road_type != 'ukendt' AND highway != 'cycleway');

UPDATE unknown_roadtype uk SET road_type = kr.road_type FROM known_roadtype kr 
WHERE ST_Touches(uk.geometry, kr.geometry) AND uk.name = kr.name;

UPDATE unknown_roadtype uk SET road_type = kr.road_type FROM known_roadtype kr 
WHERE uk.name = kr.name;

DROP VIEW unknown_roadtype;
DROP VIEW known_roadtype;

-- Updating value in column car_traffic
UPDATE osmwayskbh SET car_traffic = 'ja' 
WHERE highway ILIKE '%corridor%'   
OR highway ILIKE '%living_street%'   
OR highway ILIKE '%motorway%'    
OR highway ILIKE '%primary%'   
OR highway ILIKE '%residential%'   
OR highway ILIKE '%secondary%'     
OR highway ILIKE '%service%'   
OR highway ILIKE '%tertiary%'    
OR highway ILIKE '%trunk%'
OR road_type IN 
('motorvej', 'motortrafikvej', 'primærrute', 'sekundærrute/ringvej', 
'større vej','beboelsesvej', 'adgangsvej/parkering/privatvej_osv')
OR highway =  'unclassified' AND "name" IS NOT NULL AND "access" NOT IN  
('no', 'restricted');


-- Finding all segments with cycling infrastructure
UPDATE osmwayskbh SET cycling_infrastructure = 'ja'
WHERE "bicycle"  = 'designated'
OR highway = 'cycleway'
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
WHERE car_traffic = 'ja' AND cycling_infrastructure = 'ja';

CREATE VIEW cycleways AS (SELECT name, highway, road_type, cycling_infrastructure FROM osmwayskbh 
WHERE highway = 'cycleway');
CREATE VIEW car_roads AS (SELECT name, highway, road_type, geometry FROM osmwayskbh 
WHERE car_traffic = 'yes');

UPDATE cycleways c SET cycling_infrastructure = 'cykelinfrastruktur langs vej' 
FROM car_roads cr WHERE c.name = cr.name;

DROP VIEW cycleways;
DROP VIEW car_roads;

-- Segments where cyclists are sharing a lane with other modes of traffic
UPDATE osmwayskbh SET cycling_infrastructure = 'shared_lane' 
WHERE "cycleway" ILIKE '%shared_lane%'
OR "bicycle" ILIKE '%shared_lane%'
OR "cycleway:left" ILIKE '%shared_lane%' 
OR "cycleway:right" ILIKE '%shared_lane%'
OR "cycleway:both" ILIKE '%shared_lane%';

-- Segments with cycling infrastructure away from car streets (cykling i eget trace)
/*
The query below selects highway = cycleway which do not run along a street with car traffic
Do a join between cycling infra and roads with car traffic, find those that do not match?
*/
UPDATE TABLe osmwayskbh SET cycling_infrastructure = 'cykelinfrastruktur væk fra vej'
WHERE
-- Change - Do a buffer from streets? If more than a given segment within, classify as... 


-- OBS - ADD MORE -- classify cycling infrastructure based on cycleway? Track, lane etc.

-- Segments where cycling against the flow of traffic is allowed
UPDATE TABLE osmwayskbh SET cycling_against = 'yes'
WHERE "Cycleway" ILIKE '%opposite%'
OR "oneway:bicycle" = 'no' 
AND "oneway" IN ('yes', 'true');

-- Segments where cycling is specified as allowed or assumed allowed based on other attributes (mostly interesting for non-cycling infrastructure)
UPDATE TABLE osmwayskbh SET cycling_possible = 'yes' 
WHERE "bicycle" IN ('permissive', 'ok', 'allowed')
OR highway ILIKE '%cycleway%'
OR "cycling_infrastructure" IS NOT NULL
OR (highway IN ('path', 'track') AND 
("surface" ILIKE asphalt
OR "surface" ILIKE '%compacted%' 
OR "surface" ILIKE '%concrete%'
OR "surface" ILIKE '%paved%' 
OR "surface" ILIKE '%paving_stones%'));

-- Segments where pedestrians are allowed
UPDATE TABLE osmwayskbh SET pedestrian = 'yes' 
WHERE highway ILIKE '%pedestrian%' 
OR highway ILIKE '%path%'
OR highway ILIKEfootway '%steps%'
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