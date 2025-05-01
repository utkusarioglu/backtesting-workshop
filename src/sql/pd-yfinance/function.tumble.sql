DROP FUNCTION IF EXISTS tumble CASCADE;

CREATE FUNCTION tumble(
  ts TIMESTAMPTZ,
  window_size INTERVAL = '5 minutes',
  window_offset INTERVAL = '0 minutes'
)
  RETURNS TIMESTAMPTZ
  LANGUAGE SQL
  IMMUTABLE
AS $$
  SELECT 
    date_trunc('hour', ts) 
    + window_offset 
    + floor(
      EXTRACT(epoch FROM ts - date_trunc('hour', ts) - window_offset) 
      / EXTRACT(epoch FROM window_size)
    ) 
    * window_size;
$$;
