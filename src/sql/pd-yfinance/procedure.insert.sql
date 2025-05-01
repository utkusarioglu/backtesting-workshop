DROP TYPE IF EXISTS insert__pd_yfinance__btc_usd__row CASCADE;
DROP PROCEDURE IF EXISTS insert__pd_yfinance__btc_usd CASCADE;

CREATE TYPE insert__pd_yfinance__btc_usd__row AS (
  ts TIMESTAMPTZ,
  close_price FLOAT
);

CREATE PROCEDURE insert__pd_yfinance__btc_usd(
  input_values insert__pd_yfinance__btc_usd__row[]
)
  LANGUAGE plpgsql
  AS $$
BEGIN
  INSERT INTO
    pd_yfinance__btc_usd (ts, close_price)
  SELECT 
    i.ts,
    i.close_price
  FROM
    unnest(input_values) AS i
  ;
END;
$$;
