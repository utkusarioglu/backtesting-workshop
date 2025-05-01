-- ADDED

-- Selects the cumulative sum and average for each country
DROP VIEW IF EXISTS "gdp_country_cumulative";

CREATE VIEW "gdp_country_cumulative" AS
  WITH "cumulatives" AS (
    SELECT
      "country",
      "year",
      "value",
      round(SUM("value") OVER (
        PARTITION BY "country"
        ORDER BY "year"
        ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW
      )::numeric, 2) AS "cumulative_sum",
      round(avg("value") OVER (
        PARTITION BY "country"
        ORDER BY "year"
        ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW
      )::numeric, 2) AS "cumulative_average",
      round(avg("value") OVER (
        PARTITION BY "country"
        ORDER BY "year"
        ROWS BETWEEN 3 PRECEDING AND CURRENT ROW
      )::numeric, 2) AS "sliding_3_average"
    FROM
      "gdp"
  )
  SELECT 
    "country",
    "year",
    "value",
    "cumulative_sum",
    "cumulative_average",
    "sliding_3_average",
    ("sliding_3_average" - "cumulative_average") AS "avg_diff"
  FROM 
    "cumulatives"
;
