WITH 
  "value_max" AS (
    SELECT 
      "country",
      MAX("value") as "max"
    FROM 
      "gdp"
    GROUP BY
      "country"
  )
SELECT 
  g.id,
  m.country,
  g.year,
  ROUND(m.max::numeric, 2)
FROM 
  "value_max" AS m
INNER JOIN 
  "gdp" AS g ON g.value = m.max
ORDER BY
  max DESC
LIMIT 10
;
