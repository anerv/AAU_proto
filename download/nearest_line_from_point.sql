/*
The query finds the nearest line from a point
*/

WITH objects AS
    (SELECT
        name,
        (ST_Dump(roads.geom)).geom AS geometries
    FROM roads),

point AS
    (SELECT
        'SRID=4326;POINT(long lat)'::geometry AS point
    );

SELECT DISTINCT ON
    (ST_Distance(points_infra, wayskbh)),
    wayskbh.name
    FROM wayskbh, points_infra
        ORDER BY ST_Distance(points_infra, wayskbh)
        LIMIT 1;


select st_distance(st_closestpoint(r.the_geog::geometry, wa.location::geometry), wa.location::geometry) as cp
     , r.name
     , r.ref
     , r.ogc_fid
     , r.type
     , st_astext(wa.location)
     , wa.*
    from points_of_interest wa, roads r
    where wa.id = 'some-poi-id'
    and (r.name is not null or r.ref is not null)
    order by cp asc
    limit 10
;

SELECT DISTINCT ON (a.ident)
    a.ident, a.name As airport, n.name As closest_navaid, (ST_Distance(a.geog,n.geog)/1000)::integer As dist_km 
    FROM ch10.airports As a 
LEFT JOIN ch10.navaids As n ON ST_DWithin(a.geog, n.geog,100000)
ORDER BY a.ident, dist_km;


SELECT DISTINCT ON (p.osm_id)
    p.osm_id, p.name As point, w.name AS closest_way, ST_Distance(p.geometry,w.geometry) AS dist 
    FROM points_infra AS p
    LEFT JOIN wayskbh AS W ON ST_DWithin(p.geometry,w.geometry,5)
    ORDER BY p.osm_id, dist_km;