DROP VIEW IF EXISTS "country_stddev";

CREATE VIEW "country_stddev" AS 
  WITH 
    "avg_count" AS (
      SELECT
        "country",
        "year",
        "value",
        avg("value") OVER (PARTITION BY "country") AS "avg",
        count("value") OVER (PARTITION BY "country") AS "count"
      FROM 
        "gdp"
    ),
    "delta" AS (
      SELECT 
        "country",
        "year",
        "value",
        "avg",
        "count",
        power("value" - "avg", 2) AS "delta" 
      FROM 
        "avg_count"
    ),
    "summed" AS (
      SELECT DISTINCT
        "country",
        "year",
        "value",
        "avg",
        "count",
        "delta",
        sum("delta") OVER (PARTITION BY "country") as "sum", 
        (1.0 / ("count" - 1)) AS "n"
      FROM 
        "delta"
      WHERE 
        "count" > 1
    ) 
  SELECT
    "country",
    sqrt("sum" * "n") AS "stddev"
  FROM 
    "summed"
;
