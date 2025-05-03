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
        a1.id AS child_id,
        a2.id AS parent_id,
        CASE 
            WHEN a2.id = a1.father_id THEN 'HAS_FATHER'
            WHEN a2.id = a1.mother_id THEN 'HAS_MOTHER'
        END AS rel_type
    FROM ancestry a1
    JOIN ancestry a2 ON a2.id = a1.father_id OR a2.id = a1.mother_id
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
    COALESCE(
        jsonb_agg(
            jsonb_build_object(
                'rel_type', pr.rel_type,
                'parent_id', pr.parent_id
            )
        ) FILTER (WHERE pr.parent_id IS NOT NULL),
        '[]'::jsonb
    ) AS parents
FROM 
    cats c
    JOIN family_members fm ON c.id = fm.id
    LEFT JOIN breeds b ON c.breed_id = b.id
    LEFT JOIN cat_informations ci ON c.id = ci.cat_id
    LEFT JOIN parent_rels pr ON c.id = pr.child_id
GROUP BY 
    c.id, c.name, c.gender, c.date_of_birth, c.color_code,
    b.code, c.color, c.country_origin, c.country_current,
    ci.cattery, c.src_db
ORDER BY c.id;