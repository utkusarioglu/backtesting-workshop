CREATE TABLE IF NOT EXISTS "gdp" (
  id SERIAL,
  country TEXT,
  year INTEGER,
  value FLOAT
);

TRUNCATE TABLE "gdp";
