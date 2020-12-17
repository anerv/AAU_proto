/*
This script updates the attribute for ways data based on the land cover
*/
ALTER TABLE wayskbh 
ADD COLUMN landscape VARCHAR, 
ADD COLUMN close_to VARCHAR;


SELECT w.osm_id, l.label_modified FROM waysdk w 
    JOIN land_cover l ON ST_Intersects(w.geometry, l.geometry);

SELECT w.osm_id, ARRAY_AGG(b.name ORDER BY b.name) AS name, 
	ARRAY_AGG(b.operator ORDER BY b.name) AS operator, 
	ARRAY_AGG(b.ref ORDER BY b.name) AS ref 
	FROM waysdk w JOIN buffer b ON
	ST_ContainsProperly(b.geometry,w.geometry)
	WHERE b.route = 'bicycle' GROUP BY osm_id;