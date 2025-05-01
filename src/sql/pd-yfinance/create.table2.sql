DROP TABLE IF EXISTS pd_yfinance__btc_usd CASCADE;

CREATE TABLE pd_yfinance__btc_usd (
  id SERIAL PRIMARY KEY,
  ts TIMESTAMPTZ,
  close_price FLOAT
);
