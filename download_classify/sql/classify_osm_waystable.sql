/*
This script contains the SQL statements classifying the OSM data
The order of the queries should not be changed, 
since many updates and classifications are based on previous steps
Update table name as needed
*/

-- Creating new columns
ALTER TABLE ways_rh
ADD COLUMN car_traffic VARCHAR DEFAULT NULL,  
ADD COLUMN road_type VARCHAR DEFAULT NULL,  
ADD COLUMN cycling_infrastructure VARCHAR DEFAULT NULL,
ADD COLUMN cycling_infra_simple VARCHAR DEFAULT NULL,
ADD COLUMN path_segregation VARCHAR DEFAULT NULL,  
ADD COLUMN along_street BOOLEAN DEFAULT NULL,  
ADD COLUMN cy_infra_separated BOOLEAN DEFAULT NULL,
ADD COLUMN cycling_friendly VARCHAR DEFAULT NULL,  
ADD COLUMN cycling_allowed VARCHAR DEFAULT NULL,  
ADD COLUMN cycling_against VARCHAR DEFAULT NULL,  
ADD COLUMN elevation NUMERIC DEFAULT NULL,  
ADD COLUMN pedestrian_allowed VARCHAR DEFAULT NULL,  
ADD COLUMN on_street_park VARCHAR DEFAULT NULL,  
ADD COLUMN surface_assumed VARCHAR DEFAULT NULL,
ADD COLUMN length_ FLOAT DEFAULT NULL,
ADD COLUMN bike_length FLOAT DEFAULT NULL;  

ALTER TABLE ways_rh ADD PRIMARY KEY (osm_id);

/*
ALTER TABLE ways_rh
DROP COLUMN car_traffic, 
DROP COLUMN road_type, 
DROP COLUMN cycling_infrastructure,
DROP COLUMN cycling_infra_simple,
DROP COLUMN path_segregation, 
DROP COLUMN along_street,
DROP COLUMN cy_infra_separated,
DROP COLUMN cycling_friendly, 
DROP COLUMN cycling_allowed, 
DROP COLUMN cycling_against, 
DROP COLUMN elevation,
DROP COLUMN pedestrian_allowed,
DROP COLUMN on_street_park,
DROP COLUMN surface_assumed,
DROP COLUMN length_;
*/

--Calculating segment lengths
UPDATE ways_rh SET length_ = ST_Length(geom);

--Setting overall road type

UPDATE ways_rh SET road_type =
    (CASE
        WHEN highway ILIKE '%motorway%' THEN 'motorvej'
        WHEN highway ILIKE '%trunk%' THEN 'motortrafikvej'
        WHEN highway ILIKE '%primary%' THEN 'primaerrute'
        WHEN highway ILIKE '%secondary%' THEN 'sekundaerrute/ringvej'
        WHEN highway ILIKE '%tertiary%' THEN 'stoerre_vej'
        WHEN highway ILIKE '%residential%' THEN 'beboelsesvej'
        WHEN highway ILIKE '%service%' THEN 'adgangsvej/parkering/privatvej_osv'
        WHEN highway ILIKE '%living_street' THEN 'begraenset_biltrafik'
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
(SELECT name, osm_id, highway, road_type, geom FROM ways_rh WHERE road_type = 'ukendt');
CREATE VIEW known_roadtype 
AS (SELECT name, osm_id, highway, road_type, geom FROM ways_rh 
WHERE road_type != 'ukendt' AND highway != 'cycleway');


UPDATE unknown_roadtype uk SET road_type = kr.road_type FROM known_roadtype kr 
WHERE ST_Touches(uk.geom, kr.geom) AND uk.name = kr.name;

UPDATE unknown_roadtype uk SET road_type = kr.road_type FROM known_roadtype kr 
WHERE uk.name = kr.name AND uk.road_type = 'ukendt';

DROP VIEW unknown_roadtype;
DROP VIEW known_roadtype;

-- Updating value in column car_traffic
UPDATE ways_rh SET car_traffic = 'yes' 
WHERE road_type IN
('motorvej', 'motortrafikvej', 'primaerrute', 'sekundaerrute/ringvej', 
'stoerre vej','beboelsesvej', 'adgangsvej/parkering/privatvej_osv', 'begraenset_biltrafik')
OR highway =  'unclassified' AND "name" IS NOT NULL AND "access" NOT IN  
('no', 'restricted') OR (maxspeed::integer > 15);


-- Finding all segments with cycling infrastructure
UPDATE ways_rh SET cycling_infrastructure = 'yes'
WHERE highway = 'cycleway'
OR cycleway ILIKE '%designated%' 
OR cycleway ILIKE '%crossing%'
OR cycleway ILIKE '%lane%' 
OR cycleway ILIKE '%opposite_%' 
OR cycleway ILIKE '%track%' 
OR cycleway ILIKE '%yes%'
OR "cycleway:left" ILIKE '%lane%'
OR "cycleway:left" ILIKE '%opposite_%'
OR "cycleway:left" ILIKE '%track%'
OR "cycleway:right" ILIKE '%lane%'
OR "cycleway:right" ILIKE '%opposite_%'
OR "cycleway:right" ILIKE '%track%'
OR "cycleway:both" ILIKE '%lane%'
OR "cycleway:both" ILIKE '%opposite_%'
OR "cycleway:both" ILIKE '%track%';

UPDATE ways_rh SET cycling_infrastructure = NULL WHERE cycleway IN ('no','none');

-- Segments where cycling is specified as allowed or assumed allowed based on other attributes (mostly interesting for non-cycling infrastructure)
UPDATE ways_rh SET cycling_allowed = 'yes' 
WHERE bicycle IN ('permissive', 'ok', 'allowed', 'designated')
OR highway = 'cycleway'
OR "cycling_infrastructure" = 'yes';

UPDATE ways_rh SET cycling_allowed = 'no'
WHERE bicycle IN ('no', 'dismount', 'use_sidepath')
OR (road_type = 'motorvej' AND cycling_infrastructure IS NULL);

-- Segments where pedestrians are allowed
UPDATE ways_rh SET pedestrian_allowed = 'yes' 
WHERE highway in ('pedestrian', 'path', 'footway', 'steps')
OR foot IN ('yes', 'designated', 'permissive', 'official', 'destination')
OR sidewalk IN ('both', 'left', 'right');

/*
Categorising types of cycling infrastructure
*/
-- Updating type of cycling infrastructure based on the key cycleway
UPDATE ways_rh SET cycling_infrastructure = 'cykelsti' WHERE highway = 'cycleway';

-- Updating type of cycling infrastructure based on the key cycleway
UPDATE ways_rh SET cycling_infrastructure =
    (CASE
        WHEN cycleway = 'crossing' THEN 'cykelbane i kryds'
        WHEN cycleway = 'lane' THEN 'cykelbane_begge'
        WHEN cycleway = 'opposite_lane' THEN 'cykelbane'
        WHEN cycleway = 'opposite_track' THEN 'cykelsti' 
        WHEN cycleway = 'track' THEN 'cykelsti_begge'
        WHEN cycleway = 'shared_lane' OR bicycle = 'shared_lane' THEN 'delt_koerebane'
        ELSE cycling_infrastructure
    END)
WHERE cycling_allowed = 'yes';


/*Updating type of cycling infrastructure based on the keys cycleway:left and cycleway:right
It is assumed that right and left are not used on segments where highway = cycleway
Cycleway:left/right are only used when no type has been assigned based on the key cycleway 
(thus where the value for cycling infrastructure is still 'yes')
*/

-- Finding cycleways through intersections and roads with the same type of cycling infrastructure in both sides
UPDATE ways_rh SET cycling_infrastructure =
    (CASE
        WHEN "cycleway:left" = 'crossing' OR "cycleway:right" = 'crossing' THEN 'cykelbane i kryds'
        WHEN "cycleway:left" ILIKE '%track' AND "cycleway:right" ILIKE '%track' THEN 'cykelsti_begge'
        WHEN "cycleway:left" IN ('lane', 'opposite_lane') AND "cycleway:right" IN ('lane','opposite_lane') 
        THEN 'cykelbane_begge'
        WHEN "cycleway:both" ILIKE '%track' THEN 'cykelsti_begge'
        WHEN "cycleway:both" IN ('lane','opposite_lane') THEN 'cykelbane_begge'
        WHEN "cycleway:both" = 'shared_lane' THEN 'delt_koerebane_begge'
        ELSE cycling_infrastructure
    END)
WHERE cycling_allowed = 'yes';

-- Roads with different types of cycling infrastructure/tags in different sides
UPDATE ways_rh SET cycling_infrastructure =
    (CASE
        WHEN ("cycleway:left" ILIKE '%track' AND ("cycleway:right" = 'lane' OR "cycleway:right" = 'opposite_lane'))
            THEN 'cykelsti_venstre_cykelbane_hoejre'
        WHEN ("cycleway:right" ILIKE '%track' AND ("cycleway:left" = 'lane' OR "cycleway:left" = 'opposite_lane'))
            THEN 'cykelsti_hoejre_cykelbane_venstre'
        WHEN "cycleway:left" ILIKE '%track' AND "cycleway:right" = 'separate' 
            THEN 'cykelsti_venstre'
        WHEN "cycleway:right" ILIKE '%track' AND "cycleway:left" = 'separate' 
            THEN 'cykelsti_hoejre'
        WHEN "cycleway:left" IN ('lane','opposite_lane') AND "cycleway:right" = 'separate' 
            THEN 'cykelbane_venstre'
        WHEN "cycleway:right" IN ('lane','opposite_lane') AND "cycleway:left" = 'separate' 
            THEN 'cykelbane_hoejre'
        ELSE cycling_infrastructure
    END)
WHERE cycling_allowed = 'yes';


-- Roads with cycling infrastructure in only one side
UPDATE ways_rh SET cycling_infrastructure =
    (CASE
        WHEN "cycleway" = 'left' THEN 'cykelsti_venstre'
        WHEN "cycleway" = 'right' THEN 'cykelsti_hoejre'
        WHEN "cycleway:left" ILIKE '%track' AND ("cycleway:right" NOT IN ('lane','track','shared_lane','separate', 'opposite_lane','opposite_track')
            OR "cycleway:right" IS NULL) THEN 'cykelsti_venstre'
        WHEN "cycleway:left" IN ('lane','opposite_lane') AND ("cycleway:right" NOT IN ('lane','track','shared_lane','separate', 'opposite_lane','opposite_track')
            OR "cycleway:right" IS NULL) THEN 'cykelbane_venstre'
        WHEN "cycleway:right" ILIKE '%track' AND ("cycleway:left" NOT IN ('lane','track','shared_lane','separate', 'opposite_lane','opposite_track')
            OR "cycleway:left" IS NULL) THEN 'cykelsti_hoejre'
        WHEN "cycleway:right" IN ('lane','opposite_lane') AND ("cycleway:left" NOT IN ('lane','track','shared_lane','separate', 'opposite_lane','opposite_track')
            OR "cycleway:left" IS NULL) THEN 'cykelbane_hoejre'
        WHEN "cycleway:left" = 'shared_lane' AND ("cycleway:right" NOT IN ('lane','track','shared_lane','separate', 'opposite_lane','opposite_track')
            OR "cycleway:right" IS NULL) THEN 'delt_koerebane_venstre'
        WHEN "cycleway:right" = 'shared_lane' AND ("cycleway:left" NOT IN ('lane','track','shared_lane','separate', 'opposite_lane','opposite_track')
            OR "cycleway:left" IS NULL) THEN 'delt_koerebane_hoejre'
        ELSE cycling_infrastructure
    END)
WHERE cycling_allowed = 'yes';


-- Cycling infrastructure in one side and shared lane in the other
UPDATE ways_rh SET cycling_infrastructure =
    (CASE
        WHEN ("cycleway:left" ILIKE '%track' AND "cycleway:right" = 'shared_lane')
            THEN 'cykelsti_venstre_delt_koerebane_hoejre'
        WHEN ("cycleway:left" = 'shared_lane' AND "cycleway:right" ILIKE '%track')
            THEN 'cykelsti_hoejre_delt_koerebane_venstre'
        WHEN ("cycleway:left" IN ('lane','opposite_lane') AND "cycleway:right" = 'shared_lane')
            THEN 'cykelbane_venstre_delt_koerebane_hoejre'
        WHEN ("cycleway:left" = 'shared_lane' AND "cycleway:right" IN ('lane','opposite_lane'))
            THEN 'cykelbane_hoejre_delt_koerebane_venstre'
        ELSE cycling_infrastructure
        END)
WHERE cycling_allowed = 'yes';

-- Paths with cycling
UPDATE ways_rh SET cycling_infrastructure = 'sti_cykling_tilladt', cycling_infra_simple = 'sti_cykling_tilladt'
WHERE highway = 'path' AND (cycling_infrastructure = 'yes' OR bicycle IN ('yes','designated'));

-- Categorising path types
UPDATE ways_rh SET path_segregation =
    (CASE
        WHEN cycling_allowed = 'no' THEN 'kun gaaende'
        WHEN cycling_allowed = 'yes' AND pedestrian_allowed = 'yes' AND segregated != 'yes' THEN 'blandet cykel og gang'
        WHEN cycling_allowed = 'yes' AND pedestrian_allowed = 'yes' AND segregated = 'yes' THEN 'opdelt cykel og gang'
        ELSE 'ukendt'
    END) 
WHERE road_type IN ('sti','gangsti', 'cykelsti', 'gaagade_gangomraade');


-- Segments where cycling against the flow of traffic is allowed
UPDATE ways_rh SET cycling_against = 'yes'
WHERE cycleway ILIKE '%opposite%'
OR (oneway IN ('yes', 'true')
    AND ("oneway:bicycle" = 'no' OR "cycleway:left" ILIKE '%opposite%' 
    OR "cycleway:right" ILIKE '%opposite%')
);

-- Bike lanes and tracks with bidirectional cycling
UPDATE ways_rh SET cycling_infrastructure = 'cykelsti_dobbeltrettet'
WHERE "highway" =  'cycleway' AND (oneway = 'no' OR "oneway:bicycle" = 'no');

-- Updating a simplified version of cycling_infrastructure
UPDATE ways_rh SET cycling_infra_simple = 
    (CASE
        WHEN cycling_infrastructure IN ('cykelbane','cykelbane_begge','cykelbane_venstre, cykelbane_hoejre')
            THEN 'cykelbane'
        WHEN cycling_infrastructure IN ('cykelsti','cykelsti_begge','cykelsti_venstre', 'cykelsti_hoejre')
            THEN 'cykelsti'
        WHEN cycling_infrastructure IN ('delt_koerebane','delt_koerebane_venstre', 'delt_koerebane_hoejre', 'delt_koerebane_begge')
            THEN 'delt_koerebane'
        WHEN road_type IN ('sti','gangsti') AND cycling_infrastructure IS NULL AND cycling_allowed = 'yes'
            THEN 'sti_cykling_tilladt'
        WHEN cycling_infrastructure = 'yes' THEN 'andet'
        ELSE cycling_infrastructure
    END)
WHERE cycling_allowed = 'yes';


-- Cycle lane separated from car street (cykelsti i eget trace)
UPDATE ways_rh SET cy_infra_separated = 'true' WHERE highway = 'cycleway';
UPDATE ways_rh SET cy_infra_separated = 'false' WHERE cycling_infrastructure IS NOT NULL 
AND highway != 'cycleway';

--Determining whether the segment of cycling infrastructure runs along a street or not
-- Along a street with car traffic
UPDATE ways_rh SET along_street = 'true' WHERE car_traffic = 'yes' AND cycling_infrastructure IS NOT NULL;

-- Capturing cycleways digitized as individual ways both still running parallel to a street
CREATE VIEW cycleways AS (SELECT name, highway, road_type, cycling_infrastructure, along_street FROM ways_rh 
WHERE highway = 'cycleway');
CREATE VIEW car_roads AS (SELECT name, highway, road_type, geom FROM ways_rh 
WHERE car_traffic = 'yes');

UPDATE cycleways c SET along_street = 'true'
FROM car_roads cr WHERE c.name = cr.name;

DROP VIEW cycleways;
DROP VIEW car_roads;

-- Update car_traffic based on information in osm (rather than road_type)
UPDATE ways_rh SET car_traffic = 'no' WHERE motorcar = 'no' OR motor_vehicle = 'no';

-- Segments with on street parking
UPDATE ways_rh SET on_street_park = 'yes' 
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
UPDATE ways_rh SET surface_assumed = surface;
UPDATE ways_rh SET surface_assumed =
    (CASE 
        WHEN car_traffic = 'yes' THEN 'paved'
        WHEN highway = 'track' THEN 'unpaved'
        ELSE 'ukendt'
    END)
WHERE surface_assumed IS NULL;

--Calculating length of cycling infrafrastructure
-- Doubles the length of segments where there are cycling infrastructure in both sides
-- Shared lanes are not included
UPDATE ways_rh SET bike_length =
    CASE
        WHEN cycling_infrastructure ILIKE '%_begge'
            OR cycling_infrastructure IN ('cykelsti_venstre_cykelbane_hoejre', 'cykelsti_hoejre_cykelbane_venstre')
        THEN length_ * 2
        ELSE length_
    END
WHERE cycling_infrastructure IS NOT NULL AND cycling_infra_simple != 'delt_koerebane';

