MATCH (c:Cat)-[:BELONGS_TO_BREED]->(b:Breed)
WHERE b.breed_code <> 'unknown'
RETURN b.breed_code AS breed, COUNT(c) AS count
ORDER BY count DESC