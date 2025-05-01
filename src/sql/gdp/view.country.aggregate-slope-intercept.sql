DROP VIEW IF EXISTS "country_aggregate_slope_intercept";

CREATE VIEW "country_aggregate_slope_intercept" AS
  SELECT 
    "country",
    regr_slope("value", "year") AS "slope",
    regr_intercept("value", "year") AS "intercept"
  FROM
    "gdp"
  GROUP BY
    "country"
  ORDER BY
    "slope"
;
