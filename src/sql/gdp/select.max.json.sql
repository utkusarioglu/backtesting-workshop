with max_values AS (
  SELECT 
    "country",
    ROUND(MAX("value")::numeric, 2) as "max" 
  FROM
    "gdp"
  GROUP BY 
    "country"
) 
SELECT 
  jsonb_object_agg("country", "max")
FROM
  "max_values"
;
