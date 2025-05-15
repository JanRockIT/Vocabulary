from server.data_access.db_components import execute_commit, execute_query
from server.data_access.db_components import CONN
from constants import DEFAULT_INTERVAL, START_INTERVAL

def new_collection(
        name,
        source_language,
        target_language
):
    sql = """
    INSERT INTO vocabulary_collections (name, source_language, target_language)
    VALUES (%s, %s, %s)
    """

    execute_commit(
        connection=CONN,
        sql=sql,
        params=(name, source_language, target_language)
    )

    sql = """
    SELECT id
    FROM vocabulary_collections
    ORDER BY id DESC
    LIMIT 1;
    """

    rows = execute_query(
        connection=CONN,
        sql=sql
    )

    last_id = rows[0][0] if rows else 0

    sql = f"""
    CREATE TABLE vocabulary_collection_{last_id} (
        id SERIAL PRIMARY KEY,
        source_word TEXT NOT NULL,
        target_word TEXT NOT NULL,
        interval INT NOT NULL
    )
    """

    execute_commit(
        connection=CONN,
        sql=sql,
    )

    sql = f"""
    CREATE TABLE vocabulary_history_{last_id} (
        id INT NOT NULL,
        source_word TEXT,
        target_word TEXT,
        interval INT
    )
    """

    execute_commit(
        connection=CONN,
        sql=sql
    )

    sql = f"""
    INSERT INTO vocabulary_history_{last_id} (id)
    VALUES {', '.join(['(%s)'] * DEFAULT_INTERVAL)}
    """

    params = tuple([0 for _ in range(DEFAULT_INTERVAL)])

    execute_commit(
        connection=CONN,
        sql=sql,
        params=(params)
    )

def add_pair(
        collection_id,
        source_word,
        target_word,
        interval
):
    sql = f"""
    INSERT INTO vocabulary_collection_{collection_id} (source_word, target_word, interval)
    VALUES (%s, %s, %s)
    """

    execute_commit(
        connection=CONN,
        sql=sql,
        params=(source_word, target_word, interval)
    )

def delete_collection(id):
    sql = f"""
    DROP TABLE vocabulary_collection_{id}
    """

    execute_commit(
        connection=CONN,
        sql=sql
    )

    sql = """
    DELETE FROM vocabulary_collections
    WHERE id = %s
    """

    execute_commit(
        connection=CONN,
        sql=sql,
        params=(id,)
    )

def delete_pair(
        collection_id,
        pair_id
):
    sql = f"""
    DELETE FROM vocabulary_collection_{collection_id}
    WHERE id = %s
    """

    execute_commit(
        connection=CONN,
        sql=sql,
        params=(pair_id,)
    )

def change_collection(
        collection_id,
        columns,
        values
):
    set_clause = ", ".join(f"{col} = %s" for col in columns)

    sql = f"""
    UPDATE vocabulary_collections
    SET {set_clause}
    WHERE id = %s
    """

    params = tuple(values) + (collection_id,)

    execute_commit(
        connection=CONN,
        sql=sql,
        params=params
    )

def change_pair(
        collection_id,
        pair_id,
        columns,
        values
):
    set_clause = ", ".join(f"{col} = %s" for col in columns)

    sql = f"""
    UPDATE vocabulary_collection_{collection_id}
    SET {set_clause}
    WHERE id = %s
    """

    params = tuple(values) + (pair_id,)

    execute_commit(
        connection=CONN,
        sql=sql,
        params=params
    )

def get_collections():
    sql = """
    SELECT * FROM vocabulary_collections
    """

    rows = execute_query(
        connection=CONN,
        sql=sql
    )

    return rows

def get_collection(id):
    sql = f"""
    SELECT * FROM vocabulary_collection_{id}
    """

    rows = execute_query(
        connection=CONN,
        sql=sql
    )

    return rows

def get_pair(collection_id):
    sql = f"""
    SELECT * FROM vocabulary_collection_{collection_id}
    """

    rows = execute_query(
        connection=CONN,
        sql=sql
    )

    vocabulary_collection = rows

    sql = f"""
    SELECT * FROM vocabulary_history_{collection_id}
    """

    rows = execute_query(
        connection=CONN,
        sql=sql
    )

    vocabulary_history = rows

    for vocabulary_pair in vocabulary_collection:
        if vocabulary_pair not in vocabulary_history:
            lowest_interval_pair = vocabulary_pair
            break

    for vocabulary_pair in vocabulary_collection:
        if vocabulary_pair[3] < lowest_interval_pair[3] and vocabulary_pair not in vocabulary_history:
            lowest_interval_pair = vocabulary_pair

    sql = f"""
    DELETE FROM vocabulary_history_{collection_id}
        WHERE ctid = (
        SELECT ctid
        FROM vocabulary_history_{collection_id}
        LIMIT 1
    );    
    """

    execute_commit(
        connection=CONN,
        sql=sql
    )

    sql = f"""
    INSERT INTO vocabulary_history_{collection_id} (id, source_word, target_word, interval)
    VALUES (%s, %s, %s, %s)
    """

    execute_commit(
        connection=CONN,
        sql=sql,
        params=lowest_interval_pair
    )

    return lowest_interval_pair

def update_pair(
        collection_id,
        pair_id,
        known
):
    sql = f"""
    SELECT interval
    FROM vocabulary_collection_{collection_id}
    WHERE id = (%s)
    """

    rows = execute_query(
        connection=CONN,
        sql=sql,
        params=(pair_id,)
    )
    
    interval = rows[0][0]

    updated_interval = interval + 1 if known else START_INTERVAL

    change_pair(
        collection_id=collection_id,
        columns=['interval'],
        pair_id=pair_id,
        values=[updated_interval]
    )
