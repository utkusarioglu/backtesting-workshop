DROP VIEW IF EXISTS "country_aggregate_slope_intercept";

CREATE VIEW "country_aggregate_slope_intercept" AS
  SELECT 
    "country",
    regr_slope("value", "year"),
    regr_intercept("value", "year")
  FROM
    "gdp"
  GROUP BY
    "country"
;
