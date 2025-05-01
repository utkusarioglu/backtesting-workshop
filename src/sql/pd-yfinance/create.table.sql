DROP TABLE IF EXISTS pd_yfinance CASCADE;

CREATE TABLE pd_yfinance (
  id SERIAL PRIMARY KEY,
  ts TIMESTAMPTZ,
  close_price FLOAT
);
