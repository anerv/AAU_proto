--green urban areas 
"amenity" = 'grave_yard' OR "landuse" IN ('allotments','cemetery','churchyard' ,'harbour','park','recreation_ground','reservoir','tree','village_green', 'vineyard')
OR "leisure" IN ('dog_park','garden', 'golf_course','marina','park','playground', 'recreation_ground')

--random urban
"amenity" ILIKE 'parking%' OR "landuse" IN ('asphalt','brownfield','construction', 'greenfield')

-- build up
"leisure" IN ('building') or something with geodk

-- industrial
landuse = 'industrial'
-- stores/shops
"landuse" IN ('commercial','retail')

-- residential
"landuse" in ( 'residential' )

-- nature
landuse IN ('conservation', 'dune',  'farmland','flade_hede','forest', 'grassland','heath','meadow','orchard', 'pasture','plantation','scrub','water','wet_meadow')
OR leisure IN ('beach','beach_resort','nature_reserve')
OR natural IN ()
 
-- water
water IN 
(reservoir, river, canal, lake, spring, oxbow, lock, lagoon, water, stream, basin, dam, moat, salt pond, pond) 
OR water ILIKE '%sø%'
OR leisure IN ('beach','beach_resort')
OR natural IN ()