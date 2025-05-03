DROP VIEW IF EXISTS "country_last_and_max";

CREATE VIEW "country_last_and_max" AS
  WITH 
    last_year_values AS (
      SELECT
        g.id,
        g.country,
        g.year,
        g.value,
        'last' AS stat
      FROM gdp g
      JOIN (
        SELECT 
          country,
          MAX(year) AS year
        FROM gdp
        GROUP BY country
      ) l ON g.country = l.country AND g.year = l.year
    ),
    max_year_values AS (
      SELECT
        g.id,
        g.country,
        g.year,
        g.value,
        'max' AS stat
      FROM gdp g
      JOIN (
        SELECT 
          country,
          MAX(value) AS value
        FROM gdp
        GROUP BY country
      ) m ON g.country = m.country AND g.value = m.value
    )
  SELECT * FROM last_year_values
  UNION
  SELECT * FROM max_year_values
  ORDER BY 
    country, 
    year, 
    stat
;
