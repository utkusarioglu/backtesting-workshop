DROP VIEW IF EXISTS "country_stddev_samp";

CREATE VIEW "country_stddev_samp" AS 
  SELECT 
    "country",
    stddev_samp("value") AS "stddev"
  FROM
    "gdp"
  GROUP BY "country"
;
  
