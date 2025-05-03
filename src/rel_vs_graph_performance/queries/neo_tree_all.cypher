MATCH path = (root:Cat {id: $cat_id})-[:HAS_FATHER|HAS_MOTHER*0..{depth}]->(ancestor:Cat)
WITH root, COLLECT(DISTINCT ancestor) AS ancestors 
WITH root + ancestors AS family_nodes
UNWIND family_nodes AS cat
OPTIONAL MATCH (cat)-[:BELONGS_TO_BREED]->(breed:Breed)
OPTIONAL MATCH (cat)-[:HAS_COLOR]->(color:Color)
OPTIONAL MATCH (cat)-[:BORN_IN]->(birth_country:Country)
OPTIONAL MATCH (cat)-[:LIVES_IN]->(current_country:Country)
OPTIONAL MATCH (cat)-[:BRED_BY]->(cattery:Cattery)
OPTIONAL MATCH (cat)-[:FROM_DATABASE]->(source_db:SourceDB)
OPTIONAL MATCH (cat)-[r:HAS_FATHER|HAS_MOTHER]->(parent:Cat)
WHERE parent IN family_nodes
RETURN cat,
       breed,
       color,
       birth_country,
       current_country,
       cattery,
       source_db,
       COLLECT(DISTINCT CASE WHEN parent IS NOT NULL THEN {rel_type: TYPE(r), parent_id: parent.id} ELSE null END) AS parents