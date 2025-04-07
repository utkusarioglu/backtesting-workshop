SELECT 
  "country",
  "year",
  "value",
  "value" - avg("value") OVER (PARTITION BY "country") as "diff"
FROM 
  gdp
;
