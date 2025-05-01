DROP VIEW IF EXISTS json_nested;

CREATE VIEW json_nested AS
  SELECT 
    jsonb_object_agg(
      column_name, 
      jsonb_build_object(
        'ordinal', ordinal_position,
        'schema', table_schema,
        'table', table_name,
        'type', data_type
      )
    ) 
  FROM information_schema.columns 
  WHERE table_name = 'columns'
;

\copy (SELECT * FROM json_nested) TO '/sql/columns-data.json'
