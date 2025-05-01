SELECT jsonb_object_agg(ordinal_position, column_name)
  FROM information_schema.columns
  WHERE table_name = %s
;
