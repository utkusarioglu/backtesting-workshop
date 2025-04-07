-- Concats max value, whichever year it may be and the latest year's value

WITH 
  "m" AS (
    WITH "max_value" AS (
      SELECT 
        "country",
        max("value") AS "value"
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
      "gdp" AS g
    INNER JOIN "max_value" AS m 
      ON m.value = g.value
    ORDER BY
      "country"
    ),
  "y" AS (
    WITH "max_year" AS (
      SELECT 
        "country",
        max("year") AS "year"
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
      "gdp" AS g
    INNER JOIN "max_year" AS m
      ON m.year = g.year
    ORDER BY
      "country"
  )

SELECT * FROM "m"
UNION
SELECT * FROM "y"
ORDER BY 
  "country"
;
