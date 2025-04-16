DROP VIEW IF EXISTS "country_window_slope_intercept";

CREATE VIEW "country_window_slope_intercept" AS 
  SELECT 
    "country",
    "year",
    "value",
    regr_slope("value", "year") OVER (PARTITION BY "country") AS "slope",
    regr_intercept("value", "year") OVER (PARTITION BY "country") AS "intercept"
  FROM 
    "gdp"
;
