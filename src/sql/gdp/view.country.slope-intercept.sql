DROP VIEW IF EXISTS "country_slope_intercept";

CREATE VIEW "country_slope_intercept" AS 
  SELECT 
    "country",
    regr_slope("value", "year") AS "slope",
    regr_intercept("value", "year") AS "intercept",
    min("year") AS "start_year",
    max("year") AS "end_year"
  FROM 
    "gdp"
  GROUP BY 
    "country"
  ORDER BY 
    "slope" DESC
;
