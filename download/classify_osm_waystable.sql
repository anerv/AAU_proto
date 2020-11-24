/*
This script contains the SQL statements classifying the OSM data
The order of the queries should not be changed, 
since many updates and classifications are based on previous steps
Update table name as needed
*/

-- OBS! Find a way to add table name to script
-- Rewrite to python functions taking table name as input?

-- Creating new columns
ALTER TABLE wayskbh
ADD COLUMN car_traffic VARCHAR DEFAULT NULL, --OK
ADD COLUMN road_type VARCHAR DEFAULT NULL, -- OK
ADD COLUMN cycling_infrastructure VARCHAR DEFAULT NULL, --??
ADD COLUMN path_segregation VARCHAR DEFAULT NULL, -- OK
ADD COLUMN along_street BOOLEAN DEFAULT NULL, -- venter
ADD COLUMN cycling_friendly VARCHAR DEFAULT NULL, -- venter
ADD COLUMN cycling_allowed VARCHAR DEFAULT NULL, -- OK
ADD COLUMN cycling_against VARCHAR DEFAULT NULL, -- OK
ADD COLUMN elevation NUMERIC DEFAULT NULL, -- venter
ADD COLUMN pedestrian_allowed VARCHAR DEFAULT NULL, --OK
ADD COLUMN on_street_park VARCHAR DEFAULT NULL, --OK
ADD COLUMN surface_assumed VARCHAR DEFAULT NULL; --OK

/*
Determining overall road type. The assignment of road type is based on a hierarchy 
where the road type which usually has the highest speed and most traffic determines the type
*/

UPDATE wayskbh SET road_type =
    (CASE
        WHEN highway ILIKE '%motorway%' THEN 'motorvej'
        WHEN highway ILIKE '%trunk%' THEN 'motortrafikvej'
        WHEN highway ILIKE '%primary%' THEN 'primaerrute'
        WHEN highway ILIKE '%secondary%' THEN 'sekundaerrute/ringvej'
        WHEN highway ILIKE '%tertiary%' THEN 'stoerre vej'
        WHEN highway ILIKE '%residential%' THEN 'beboelsesvej'
        WHEN highway ILIKE '%service%' THEN 'adgangsvej/parkering/privatvej_osv'
        WHEN highway ILIKE '%living_street' THEN 'begraenset biltrafik'
        WHEN highway ILIKE '%pedestrian%' THEN 'gaagade_gangomraade'
        WHEN highway ILIKE '%path%' THEN 'sti'
        WHEN highway ILIKE '%cycleway%' THEN 'cykelsti'
        WHEN highway ILIKE '%footway%' THEN 'gangsti'
        WHEN highway ILIKE '%track%' THEN 'sti'
        WHEN highway ILIKE '%steps%' THEN 'trappe'
        WHEN highway = 'elevator' OR highway = 'corridor' THEN 'ikke_vej'
        ELSE 'ukendt'
    END);

-- Limiting number of road segments with road type 'unknown'
CREATE VIEW unknown_roadtype AS 
(SELECT name, osm_id, highway, road_type, geometry FROM wayskbh WHERE road_type = 'ukendt');
CREATE VIEW known_roadtype 
AS (SELECT name, osm_id, highway, road_type, geometry FROM wayskbh 
WHERE road_type != 'ukendt' AND highway != 'cycleway');


UPDATE unknown_roadtype uk SET road_type = kr.road_type FROM known_roadtype kr 
WHERE ST_Touches(uk.geometry, kr.geometry) AND uk.name = kr.name;

--UPDATE unknown_roadtype uk SET road_type = kr.road_type FROM known_roadtype kr 
--WHERE uk.name = kr.name;

DROP VIEW unknown_roadtype;
DROP VIEW known_roadtype;

-- Updating value in column car_traffic
UPDATE wayskbh SET car_traffic = 'yes' 
WHERE road_type IN
('motorvej', 'motortrafikvej', 'primaerrute', 'sekundaerrute/ringvej', 
'stoerre vej','beboelsesvej', 'adgangsvej/parkering/privatvej_osv')
OR highway =  'unclassified' AND "name" IS NOT NULL AND "access" NOT IN  
('no', 'restricted');


-- Finding all segments with cycling infrastructure
UPDATE wayskbh SET cycling_infrastructure = 'yes'
WHERE "bicycle"  = 'designated'
OR highway = 'cycleway'
OR cycleway ILIKE '%designated%' 
OR cycleway ILIKE '%crossing%'
OR cycleway ILIKE '%lane%' 
OR cycleway ILIKE '%opposite%' 
OR cycleway ILIKE '%track%' 
OR cycleway ILIKE '%yes%'
OR "cycleway:left" ILIKE '%lane%'
OR "cycleway:left" ILIKE '%opposite%'
OR "cycleway:left" ILIKE '%track%'
OR "cycleway:right" ILIKE '%lane%'
OR "cycleway:right" ILIKE '%opposite%'
OR "cycleway:right" ILIKE '%track%'
OR "cycleway:both" ILIKE '%lane%'
OR "cycleway:both" ILIKE '%opposite%'
OR "cycleway:both" ILIKE '%track%';

-- Segments where cycling is specified as allowed or assumed allowed based on other attributes (mostly interesting for non-cycling infrastructure)
UPDATE wayskbh SET cycling_allowed = 'yes' 
WHERE bicycle IN ('permissive', 'ok', 'allowed', 'designated')
OR highway = 'cycleway'
OR "cycling_infrastructure" = 'yes';

UPDATE wayskbh SET cycling_allowed = 'no'
WHERE bicycle IN ('no', 'dismount', 'use_sidepath')
OR (road_type = 'motorvej' AND cycling_infrastructure IS NULL);

-- Segments where pedestrians are allowed
UPDATE wayskbh SET pedestrian_allowed = 'yes' 
WHERE highway in ('pedestrian', 'path', 'footway', 'steps')
OR foot IN ('yes', 'designated', 'permissive', 'official', 'destination')
OR sidewalk IN ('both', 'left', 'right');

/*
Categorising types of cycling infrastructure
*/
-- Updating type of cycling infrastructure based on the key cycleway
UPDATE wayskbh SET cycling_infrastructure = 'cykelsti' WHERE highway = 'cycleway';

-- Updating type of cycling infrastructure based on the key cycleway
UPDATE wayskbh SET cycling_infrastructure =
    (CASE
        WHEN cycleway = 'crossing' THEN 'cykelbane i kryds'
        WHEN cycleway = 'lane' THEN 'cykelbane'
        WHEN cycleway = 'opposite_lane' THEN 'cykelbane mod ensretning'
        WHEN cycleway = 'opposite_track' THEN 'cykelsti mod ensretning'
        WHEN cycleway = 'track' THEN 'cykelsti'
        WHEN cycleway = 'shared_lane' OR bicycle = 'shared_lane' THEN 'delt koerebane'
        ELSE cycling_infrastructure
    END)
WHERE cycling_allowed = 'yes';


/*Updating type of cycling infrastructure based on the keys cycleway:left and cycleway:right
It is assumed that right and left are not used on segments where highway = cycleway
Cycleway:left/right are only used when no type has been assigned based on the key cycleway 
(thus where the value for cycling infrastructure is still 'yes')
*/

-- Finding cycleways through intersections and roads with the same type of cycling infrastructure in both sides
UPDATE wayskbh SET cycling_infrastructure =
    (CASE
        WHEN "cycleway:left" = 'crossing' OR "cycleway:right" = 'crossing' THEN 'cykelbane i kryds'
        WHEN "cycleway:left" = 'lane' AND "cycleway:right" = 'lane' THEN 'cykelbane'
        WHEN "cycleway:left" = 'track' AND "cycleway:right" = 'track' THEN 'cykelsti'
        ELSE cycling_infrastructure
    END)
WHERE cycling_allowed = 'yes';

-- Roads with different types of cycling infrastructure in different sides
UPDATE wayskbh SET cycling_infrastructure =
    (CASE
        WHEN ("cycleway:left" ILIKE '%track' AND ("cycleway:right" = 'lane' OR "cycleway:right" = 'opposite_lane')) 
            OR ("cycleway:right" ILIKE '%track' AND ("cycleway:left" = 'lane' OR "cycleway:right" = 'opposite_lane'))
            THEN 'cykelsti_cykelbane'
        ELSE cycling_infrastructure
    END)
WHERE cycling_allowed = 'yes';

-- Roads with only cycling infrastructure in one side
-- Add is null!
UPDATE wayskbh SET cycling_infrastructure =
    (CASE
        WHEN "cycleway:left" = 'track' AND ("cycleway:right" NOT IN ('lane','track','shared_lane','separate', 'opposite_lane','opposite_track')
            OR "cycleway:right" IS NULL) THEN 'cykelsti_enkeltsidet'
        WHEN "cycleway:left" = 'lane' AND "cycleway:right" NOT IN ('lane','track','shared_lane','separate', 'opposite_lane','opposite_track')
            THEN 'cykelbane_enkeltsidet'
        WHEN "cycleway:right" = 'track' AND "cycleway:left" NOT IN ('lane','track','shared_lane','separate', 'opposite_lane','opposite_track')
            THEN 'cykelsti_enkeltsidet'
        WHEN "cycleway:right" = 'lane' AND "cycleway:left" NOT IN ('lane','track','shared_lane','separate', 'opposite_lane','opposite_track')
            THEN 'cykelbane_enkeltsidet'
        ELSE cycling_infrastructure
    END)
WHERE cycling_allowed = 'yes';


-- Cycling infrastructure in one side and shared lane in the other
UPDATE wayskbh SET cycling_infrastructure =
    (CASE
        WHEN ("cycleway:left" ILIKE '%track' AND "cycleway:right" = 'shared_lane') 
            OR ("cycleway:left" = 'shared_lane' AND "cycleway:right" ILIKE '%track')
            THEN 'cykelsti_og_delt_bane'
        WHEN ("cycleway:left" IN ('lane','opposite_lane') AND "cycleway:right" = 'shared_lane') 
            OR ("cycleway:left" = 'shared_lane' AND "cycleway:right" IN ('lane','opposite_lane'))
            THEN 'cykelbane_og_delt_bane'
        ELSE cycling_infrastructure
        END)
WHERE cycling_allowed = 'yes';

-- Categorising path types
UPDATE wayskbh SET path_segregation =
    (CASE
        WHEN cycling_allowed = 'no' THEN 'kun gaaende'
        WHEN cycling_allowed = 'yes' AND pedestrian_allowed = 'yes' AND segregated != 'yes' THEN 'blandet cykel og gang'
        WHEN cycling_allowed = 'yes' AND pedestrian_allowed = 'yes' AND segregated = 'yes' THEN 'opdelt cykel og gang'
        ELSE 'ukendt'
    END) 
WHERE road_type IN ('sti','gangsti', 'cykelsti', 'gaagade_gangomraade');


-- Segments where cycling against the flow of traffic is allowed
UPDATE wayskbh SET cycling_against = 'yes'
WHERE cycleway ILIKE '%opposite%'
OR (oneway IN ('yes', 'true')
AND ("oneway:bicycle" = 'no' OR "cycleway:left" ILIKE '%opposite%' 
    OR "cycleway:right" ILIKE '%opposite%')
);


-- Segments with on street parking
UPDATE wayskbh SET on_street_park = 'yes' 
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


--Determining surface based on segment type
UPDATE wayskbh SET surface_assumed = surface;
UPDATE wayskbh SET surface_assumed =
    (CASE 
        WHEN car_traffic = 'yes' THEN 'paved'
        WHEN highway = 'track' THEN 'unpaved'
        ELSE 'ukendt'
    END)
WHERE surface_assumed IS NULL;



/* Determining whether the segment of cycling infrastructure runs along a street or not

-- Potentially combine with step that connects road ids from GeoDK data, or other data source
-- Add something here - use a buffer to find segments which are along a street? 
-- If more than xxx % of segment within a xx meter buffer of car street, then along a street
-- For all in ('sti','gangsti','cykel- og gangsti', 'cykelsti', 'gaagade_gangomraade', 'trappe')

UPDATE wayskbh SET cycling_infrastructure = 'cykelinfrastruktur langs vej'
WHERE car_traffic = 'yes' AND cycling_infrastructure = 'yes';

CREATE VIEW cycleways AS (SELECT name, highway, road_type, cycling_infrastructure FROM wayskbh 
WHERE highway = 'cycleway');
CREATE VIEW car_roads AS (SELECT name, highway, road_type, geometry FROM wayskbh 
WHERE car_traffic = 'yes');

UPDATE cycleways c SET cycling_infrastructure = 'cykelinfrastruktur langs vej' 
FROM car_roads cr WHERE c.name = cr.name;

DROP VIEW cycleways;
DROP VIEW car_roads;

*/


-- Cycling friendly segments
/*
Should both be based on elevation, surface, speed, number of lanes, presence of cycling infrastructure
cycle friendly paths etc


OR (highway IN ('path', 'track') AND 
("surface" ILIKE asphalt
OR "surface" ILIKE '%compacted%' 
OR "surface" ILIKE '%concrete%'
OR "surface" ILIKE '%paved%' 
OR "surface" ILIKE '%paving_stones%'));

*/

-- Finally, dealing with unclassified segments