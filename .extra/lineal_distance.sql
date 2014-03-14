-- lineal_distance defined on plpythonu (python2)
-- benchmark: Total runtime: 0.148 ms

CREATE OR REPLACE FUNCTION lineal_distance(origin point, curr point) RETURNS double precision AS $$
    import re, sys, math

    rx_point = re.compile(r'\(([\d\.\-]*),\s*([\d\.\-]*)\)')
    res = rx_point.search(origin)
    lat0, lon0 = map(float, res.groups())
    lat0, lon0 = math.radians(lat0), math.radians(lon0)

    res = rx_point.search(curr)
    lat1, lon1 = map(float, res.groups())
    lat1, lon1 = math.radians(lat1), math.radians(lon1)

    return 6371 * math.acos((math.cos(lat0) * math.cos(lat1) * math.cos(lon1 - lon0)) + (math.sin(lat0) * math.sin(lat1)))
$$ LANGUAGE plpythonu;

-- lineal_distance defined on simple sql language
-- benchmark: Total runtime: 0.038 ms

CREATE OR REPLACE FUNCTION lineal_distance(IN origin point, IN curr point) RETURNS double precision
AS 'SELECT 6371 * acos(
    (cos(radians($1[0])) * cos(radians($2[0])) * cos(radians($2[1]) - radians($1[1]))) + 
    (sin(radians($1[0])) * sin(radians($2[0]))))' 
LANGUAGE SQL;


-- lineal_distance defined on plpgsql
-- benchmark: Total runtime: 0.074 ms

CREATE OR REPLACE FUNCTION lineal_distance(origin point, curr point) RETURNS double precision AS $$
DECLARE
    result double precision;
BEGIN
    result := 6371 * acos(
        (cos(radians(origin[0])) * cos(radians(curr[0])) * cos(radians(curr[1]) - radians(origin[1]))) +
        (sin(radians(origin[0])) * sin(radians(curr[0]))));
    RETURN result;
END; $$ LANGUAGE plpgsql IMMUTABLE;
