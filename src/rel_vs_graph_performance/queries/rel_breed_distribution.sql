SELECT 
    b.code AS breed, 
    COUNT(c.id) AS count
FROM 
    cats c
JOIN 
    breeds b ON c.breed_id = b.id
WHERE 
    b.code != 'unknown'
GROUP BY 
    b.code
ORDER BY 
    count DESC;