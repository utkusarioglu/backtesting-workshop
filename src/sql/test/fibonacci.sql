-- recursive fibonacci with temp table as memo

-- TODO some kind of namespacing to prevent `fibonacci_recurse` 
-- function to be called by anything other than `fibonacci` method

DROP FUNCTION IF EXISTS "fibonacci"("target" SMALLINT);
DROP FUNCTION IF EXISTS "fibonacci_recurse"("target" SMALLINT);

CREATE FUNCTION "fibonacci_recurse"("target" SMALLINT)
  RETURNS INTEGER
  LANGUAGE plpgsql
  AS $$
DECLARE
  current INTEGER;
BEGIN
  SELECT "value" INTO "current" FROM "fibonacci_memo" WHERE "index" = "target";

  IF FOUND THEN
    RETURN "current";
  END IF;

  IF "target" <= 1 THEN
    current := "target";
  ELSE
    current := fibonacci_recurse(("target" - 1)::SMALLINT) + fibonacci_recurse(("target" - 2)::SMALLINT);
  END IF;

  INSERT INTO "fibonacci_memo" ("index", "value") VALUES ("target", "current");

  RETURN current;
END;
$$;

CREATE FUNCTION "fibonacci"("target" SMALLINT)
  RETURNS INTEGER
  LANGUAGE plpgsql
  AS $$
BEGIN
  CREATE TEMP TABLE IF NOT EXISTS "fibonacci_memo" (
    "index" SMALLINT PRIMARY KEY,
    "value" INTEGER
  ) ON COMMIT PRESERVE ROWS;

  RETURN fibonacci_recurse("target");
END;
$$;

SELECT fibonacci(3::SMALLINT);
SELECT fibonacci(4::SMALLINT);
SELECT fibonacci(5::SMALLINT);
SELECT fibonacci(20::SMALLINT);
SELECT fibonacci(30::SMALLINT);

SELECT "index", "value" FROM "fibonacci_memo" ORDER BY "index";
