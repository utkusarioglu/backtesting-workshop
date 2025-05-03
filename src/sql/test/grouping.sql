DROP VIEW IF EXISTS sample_query;
DROP PROCEDURE IF EXISTS create_data;
DROP TABLE IF EXISTS sample_data;

CREATE TEMP TABLE sample_data (
  id SERIAL PRIMARY KEY,
  country TEXT,
  year TIMESTAMPTZ,
  value FLOAT
);

CREATE TYPE row_data AS (
  country TEXT,
  year INTEGER,
  value FLOAT
);

CREATE PROCEDURE create_data()
  LANGUAGE plpgsql
  AS $$
DECLARE 
  input_rows row_data[] = ARRAY[
    ROW('USA', 2001, 3),
    ROW('USA', 2002, 4),
    ROW('USA', 2003, 5),
    ROW('GER', 2008, 3),
    ROW('GER', 2009, 4),
    ROW('GER', 2010, 5)
  ];
BEGIN
  INSERT INTO 
    sample_data (country, year, value)
  SELECT 
    r.country,
    (r.year || '-01-01')::TIMESTAMPTZ,
    value::FLOAT
  FROM 
    unnest(input_rows) as r
  ;
END;
$$;

CREATE VIEW sample_query AS 
  WITH
    country_max AS (
      SELECT 
        country,
        max(value) AS max
      FROM 
        sample_data
      GROUP BY
        country
    )
  SELECT 
    t.id,
    t.country,
    t.year,
    t.value
  FROM
    country_max AS m
  LEFT JOIN 
    sample_data AS t ON 
      t.value = m.max 
      AND 
      t.country = m.country
;

CALL create_data();
SELECT * FROM sample_query;
-- SELECT * FROM sample_data;
