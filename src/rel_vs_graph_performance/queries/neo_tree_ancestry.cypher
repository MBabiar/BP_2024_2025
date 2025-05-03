MATCH path = (c:Cat {id: 2})-[:HAS_FATHER|HAS_MOTHER*1..1000]->(ancestor:Cat)
RETURN c.id AS source_id,
       ancestor.id AS ancestor_id,
       length(path) AS depth,
       type(last(relationships(path))) AS relationship_type