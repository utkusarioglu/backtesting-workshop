SELECT 
  array_agg("column_name")
FROM 
  information_schema.columns
WHERE 
  table_name = %s
;
