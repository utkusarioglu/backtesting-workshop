DROP VIEW IF EXISTS "country_aggregate_merge_slope_intercept";

CREATE VIEW "country_aggregate_merge_slope_intercept" AS
  WITH
    "regr" AS (
      SELECT 
        "country",
        regr_slope("value", "year") AS "slope",
        regr_intercept("value", "year") AS "intercept"
      FROM 
        "gdp"
      GROUP BY
        "country"
    )
  SELECT 
    g."country",
    g.year,
    g.value,
    r."slope",
    r."intercept"
  FROM 
    "gdp" AS g
  LEFT OUTER JOIN "regr" AS "r" 
    ON r.country = g.country
;
