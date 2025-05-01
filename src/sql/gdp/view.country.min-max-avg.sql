-- View for selecting min max and average values for each country

DROP VIEW IF EXISTS "country_min_max_avg";

CREATE VIEW "country_min_max_avg" AS
  WITH "country_min" AS (
    SELECT 
      "country",
      min("value"),
      max("value"),
      avg("value"),
      
      FROM 
        "gdp"
      GROUP BY
        "country"
  )
  SELECT
    "country",
    "min",
    "max",
    "avg",
    "max" - "min" as "Spread"
  FROM 
    "country_min"
  ;
  
