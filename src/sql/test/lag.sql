DROP TABLE IF EXISTS things;

CREATE TEMP TABLE things (
  id SERIAL PRIMARY KEY,
  amount INTEGER
);

INSERT INTO
  things(amount)
VALUES
  (1),
  (2),
  (3),
  (4),
  (5),
  (6)
;

SELECT
  COALESCE(amount, 0) 
    + COALESCE(lag(amount) OVER (ORDER BY id), 0) 
    + COALESCE(lag(amount, 2) OVER (ORDER BY id), 0) 
    AS "lagged",
  sum(amount) OVER (
    ORDER BY id 
    ROWS BETWEEN 2 PRECEDING AND CURRENT ROW
  ) AS "summed"
FROM
  things;
