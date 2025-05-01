SELECT 
  country,
  regr_intercept(value, year) AS "intercept",
  regr_slope(value, year) AS "slope"
FROM 
  gdp
GROUP BY
  country 
ORDER BY 
  slope DESC
;
