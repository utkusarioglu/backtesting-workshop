DROP VIEW IF EXISTS "country_last_and_max";

CREATE VIEW "country_last_and_max" AS
  WITH 
    "last_year_values" AS (
      WITH "last_year" AS (
        SELECT 
          "country",
          max("year") as "year"
        FROM 
          "gdp"
        GROUP BY
          "country"
      )
      SELECT
        g.id,
        g.country,
        g.year,
        g.value
      FROM
        "last_year" AS l
      JOIN
        "gdp" AS g ON 
          g.year = l.year
          AND
          g.country = l.country
    ),
    "max_year_values" AS (
      WITH "max_year" AS (
        SELECT 
          "country",
          max("value") as "value"
        FROM 
          "gdp"
        GROUP BY
          "country"
      )
      SELECT
        g.id,
        g.country,
        g.year,
        g.value
      FROM
        "max_year" AS m
      JOIN 
        "gdp" AS g ON 
          g.value = m.value
          AND
          g.country = m.country
    )
    SELECT 
      *,
      'last' AS "stat"
    FROM "last_year_values"
    UNION
    SELECT 
      *,
      'min' AS "stat"
    FROM "max_year_values"
    ORDER BY
      "country",
      "year",
      "stat"
;
