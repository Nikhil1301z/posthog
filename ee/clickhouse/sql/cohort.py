from .clickhouse import COLLAPSING_MERGE_TREE, STORAGE_POLICY, table_engine

CALCULATE_COHORT_PEOPLE_SQL = """
SELECT distinct_id FROM ({latest_distinct_id_sql}) where {query} AND team_id = %(team_id)s
"""

CREATE_COHORTPEOPLE_TABLE_SQL = """
CREATE TABLE cohortpeople
(
    person_id UUID,
    cohort_id Int64,
    team_id Int64,
    sign Int8
) ENGINE = {engine}
Order By (team_id, cohort_id, person_id)
{storage_policy}
""".format(
    engine=table_engine("cohortpeople", "sign", COLLAPSING_MERGE_TREE), storage_policy=STORAGE_POLICY
)

DROP_COHORTPEOPLE_TABLE_SQL = """
DROP TABLE cohortpeople
"""

REMOVE_PEOPLE_NOT_MATCHING_COHORT_ID_SQL = """
INSERT INTO cohortpeople
SELECT person_id, cohort_id, %(team_id)s as team_id,  -1 as _sign
FROM cohortpeople
JOIN (
    SELECT id, argMax(properties, person._timestamp) as properties, sum(is_deleted) as is_deleted FROM person WHERE team_id = %(team_id)s GROUP BY id
) as person ON (person.id = cohortpeople.person_id)
WHERE cohort_id = %(cohort_id)s
AND 
    (
        person.is_deleted = 1 OR NOT ({cohort_filter})
    )
"""

INSERT_PEOPLE_MATCHING_COHORT_ID_SQL = """
INSERT INTO cohortpeople
    SELECT id, %(cohort_id)s as cohort_id, %(team_id)s as team_id, 1 as _sign
    FROM (
        SELECT id, argMax(properties, person._timestamp) as properties, sum(is_deleted) as is_deleted FROM person WHERE team_id = %(team_id)s GROUP BY id
    ) as person
    LEFT JOIN cohortpeople ON (person.id = cohortpeople.person_id)
    WHERE cohortpeople.person_id = '00000000-0000-0000-0000-000000000000'
    AND person.is_deleted = 0
    AND {cohort_filter}
"""

GET_DISTINCT_ID_BY_ENTITY_SQL = """
SELECT distinct_id FROM events WHERE team_id = %(team_id)s {date_query} AND {entity_query}
"""
