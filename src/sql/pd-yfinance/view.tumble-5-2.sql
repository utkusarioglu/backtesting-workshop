DROP VIEW IF EXISTS tumble_5_2;

CREATE VIEW tumble_5_2 AS 
  WITH 
    tumble_groups AS (
      SELECT 
        id,
        tumble(ts, '5 minutes'::INTERVAL, '2 minutes'::INTERVAL) AS tumble_group
      FROM 
        pd_yfinance
    )
  SELECT 
    t.*,
    row_number() OVER (PARTITION BY tumble_group ORDER BY ts) AS "row_number",
    p.ts,
    p.close_price
  FROM 
    tumble_groups AS t
  INNER JOIN
    pd_yfinance AS p ON p.id = t.id
  ORDER BY
    id
;
    