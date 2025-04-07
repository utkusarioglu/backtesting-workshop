DROP FUNCTION IF EXISTS "latest_year";

CREATE FUNCTION "latest_year"()
  RETURNS SETOF "gdp"
  LANGUAGE PLPGSQL
  AS $$
BEGIN
  RETURN QUERY (
    WITH "max_years_by_country" AS (
      SELECT 
        "country",
        MAX("year") AS "year"
      FROM 
        "gdp"
      GROUP BY
        "country"
    ) 
    SELECT
      g.id,
      g.country,
      g.year,
      g.value
    FROM 
      "max_years_by_country" AS m
    JOIN
      "gdp" AS g ON 
        g.year = m.year 
        AND 
        g.country = m.country
    ORDER BY
      g.country
  );
END;
$$;
