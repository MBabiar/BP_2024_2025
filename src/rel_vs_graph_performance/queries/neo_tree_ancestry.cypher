MATCH path = (c:Cat {id: $cat_id})-[:HAS_FATHER|HAS_MOTHER*1..{depth}]->(ancestor:Cat)
RETURN c.id AS source_id,
       ancestor.id AS ancestor_id,
       length(path) AS depth,
       type(last(relationships(path))) AS relationship_type