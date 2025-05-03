DROP FUNCTION IF EXISTS tumble;
DROP TABLE IF EXISTS events;

CREATE TEMP TABLE events (
  id SERIAL PRIMARY KEY,
  event_time TIMESTAMP NOT NULL,
  num INTEGER
);

INSERT INTO 
  events (event_time, num) 
VALUES
  ('2025-04-27 10:01:23', 1),
  ('2025-04-27 10:03:45', 2),
  ('2025-04-27 10:06:12', 3),
  ('2025-04-27 10:08:55', 4),
  ('2025-04-27 10:11:05', 5),
  ('2025-04-27 10:15:00', 6),
  ('2025-04-27 10:18:30', 7)
;


CREATE FUNCTION tumble(
  "ts" TIMESTAMP,
  "window_size" INTERVAL = '10 minutes',
  "offset" INTERVAL = '0 minutes'
)
RETURNS TIMESTAMP
LANGUAGE SQL
IMMUTABLE
AS $$
  SELECT date_trunc('hour', ts) 
    + "offset" 
    + floor(EXTRACT(epoch FROM ts - date_trunc('hour', ts) - "offset") 
    / EXTRACT(epoch FROM window_size)) 
    * window_size
$$;



SELECT
  tumble(event_time) AS window_start,
  COUNT(*) AS events_in_window,
  max(num) AS max_value
FROM 
  events
GROUP BY 
  window_start
ORDER BY 
  window_start
;
