WITH RECURSIVE ancestry AS (
    SELECT 
        c.id, 
        ref.father_id, 
        ref.mother_id,
        0 AS depth,
        ARRAY[c.id] AS path
    FROM cats c
    LEFT JOIN cat_references ref ON c.id = ref.cat_id
    WHERE c.id = %(cat_id)s
    UNION ALL
    SELECT 
        c.id,
        parent_ref.father_id,
        parent_ref.mother_id,
        a.depth + 1,
        a.path || c.id
    FROM cats c
    JOIN cat_references parent_ref ON c.id = parent_ref.cat_id
    JOIN ancestry a ON c.id = a.father_id OR c.id = a.mother_id
    WHERE a.depth < %(depth)s
),
family_members AS (
    SELECT DISTINCT id FROM ancestry
),
parent_rels AS (
    SELECT 
        a.id AS child_id,
        a.father_id AS parent_id,
        'HAS_FATHER' AS rel_type
    FROM ancestry a
    WHERE a.father_id IS NOT NULL
    AND a.father_id IN (SELECT id FROM family_members)
    
    UNION ALL
    
    SELECT 
        a.id AS child_id,
        a.mother_id AS parent_id,
        'HAS_MOTHER' AS rel_type
    FROM ancestry a
    WHERE a.mother_id IS NOT NULL
    AND a.mother_id IN (SELECT id FROM family_members)
)
SELECT
    c.id AS cat_id, 
    c.name, 
    c.gender, 
    c.date_of_birth,
    b.code AS breed_code,
    NULL AS breed_full_name,
    c.color_code,
    c.color AS color_definition,
    c.country_origin AS birth_country_name,
    NULL AS birth_country_alpha_2,
    c.country_current AS current_country_name,
    NULL AS current_country_alpha_2,
    ci.cattery AS cattery_name,
    c.src_db AS source_db_name,
    pr.rel_type,
    pr.parent_id
FROM 
    cats c
    JOIN family_members fm ON c.id = fm.id
    LEFT JOIN breeds b ON c.breed_id = b.id
    LEFT JOIN cat_informations ci ON c.id = ci.cat_id
    LEFT JOIN parent_rels pr ON c.id = pr.child_id
ORDER BY c.id, pr.rel_type;