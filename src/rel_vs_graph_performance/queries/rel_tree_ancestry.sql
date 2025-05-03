WITH RECURSIVE family_tree AS (
    SELECT cat_id, father_id, mother_id, 1 AS depth, ARRAY[cat_id] AS path
    FROM cat_references
    WHERE cat_id = 2
    UNION ALL
    SELECT cr.cat_id, cr.father_id, cr.mother_id, ft.depth + 1 AS depth, ft.path || cr.cat_id AS path
    FROM cat_references cr
    JOIN family_tree ft ON cr.cat_id = ft.father_id OR cr.cat_id = ft.mother_id
    WHERE ft.depth < 1000
)
SELECT 2 AS source_id, parent_id AS ancestor_id, ft.depth, rel_type AS relationship_type
FROM (
    SELECT cat_id, father_id AS parent_id, depth, 'HAS_FATHER' AS rel_type
    FROM family_tree
    WHERE depth >= 1 AND depth <= 1000 AND father_id IS NOT NULL
    UNION ALL
    SELECT cat_id, mother_id AS parent_id, depth, 'HAS_MOTHER' AS rel_type
    FROM family_tree
    WHERE depth >= 1 AND depth <= 1000 AND mother_id IS NOT NULL
) AS ft
WHERE ft.parent_id IS NOT NULL
ORDER BY depth, ancestor_id, relationship_type;