ALTER TABLE test ADD COLUMN wkt VARCHAR;
UPDATE test SET wkt = St_AsText(ST_Transform(geom,4326));