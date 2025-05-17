from db_components import execute_commit, execute_query
from constants import (
    DATABASE_INTERVAL,
    INTERVAL_RESET,
    INTERVAL_START,
    STATUS_COLLECTION_DEFAULT,
    STATUS_PAIR_DEFAULT,
    STATUS_DELETED
)

# get
def get_collections() -> list[tuple]:
    sql: str = """
    SELECT *
    FROM vocabulary_collections;
    """

    rows: list[tuple] = execute_query(
        sql=sql
    )

    return rows

def get_collection(
        collection_id: int
) -> tuple:
    sql: str = """
    SELECT *
    FROM vocabulary_collections
    WHERE id = %s
    LIMIT 1;
    """

    rows: list[tuple] = execute_query(
        sql=sql,
        params=(collection_id,)
    )

    return rows[0] if rows else None

def get_pairs(
        collection_id: int
) -> tuple:
    sql: str = """
    SELECT *
    FROM vocabulary_pairs
    WHERE collection_id = %s;
    """

    rows: list[tuple] = execute_query(
        sql=sql,
        params=(collection_id,)
    )

    return rows

def get_pair(
        collection_id: int,
        pair_id: int
) -> tuple:
    sql: str = """
    SELECT *
    FROM vocabulary_pairs
    WHERE collection_id = %s
    AND id = %s
    LIMIT 1;
    """

    params: tuple = (collection_id, pair_id)

    rows: list[tuple] = execute_query(
        sql=sql,
        params=params
    )

    return rows[0] if rows else None

def get_all_history() -> list[tuple]:
    sql: str = """
    SELECT *
    FROM vocabulary_history;
    """

    rows: list[tuple] = execute_query(
        sql=sql
    )

    return rows

def get_collection_history(
        collecion_id: int
) -> list[tuple]:
    sql: str = """
    SELECT *
    FROM vocabulary_history
    WHERE collection_id = %s;
    """

    rows: list[tuple] = execute_query(
        sql=sql,
        params=(collecion_id,)
    )

    return rows

# add
def add_collection(
        collection_name: str,
        source_language: str,
        target_language: str
) -> int:
    sql: str = """
    INSERT INTO vocabulary_collections
    (name, source_language, target_language, status)
    VALUES (%s, %s, %s, %s)
    RETURNING id;
    """

    status: int = STATUS_COLLECTION_DEFAULT

    params: tuple = (
        collection_name,
        source_language,
        target_language,
        status
    )

    rows: list[tuple] = execute_query(
        sql=sql,
        params=params
    )

    new_id: int = rows[0][0]

    return new_id

def add_pair(
        collection_id: int,
        source_word: str,
        target_word: str
) -> None:
    sql: str = """
    INSERT INTO vocabulary_pairs
    (collection_id, source_word, target_word, status, interval)
    VALUES (%s, %s, %s, %s, %s);
    """

    status: int = STATUS_PAIR_DEFAULT
    interval: int = INTERVAL_START

    params: tuple = (
        collection_id,
        source_word,
        target_word,
        status,
        interval
    )

    execute_commit(
        sql=sql,
        params=params
    )

def add_history(
      collection_id: int,
      pair_id: int  
) -> None:
    sql: str = """
    INSERT INTO vocabulary_history
    (collection_id, pair_id)
    VALUES (%s, %s);
    """
    
    params: tuple = (
        collection_id,
        pair_id
    )

    execute_commit(
        sql=sql,
        params=params
    )

# delete
def delete_collection(
        collection_id: int
) -> None:
    sql: str = """
    UPDATE vocabulary_collections
        SET status = %s
    WHERE id = %s;
    """

    status: int = STATUS_DELETED

    params: tuple = (
        status,
        collection_id
    )

    execute_commit(
        sql=sql,
        params=params
    )

def delete_pair(
        collection_id: int,
        pair_id: int
) -> None:
    sql: str = """
    UPDATE vocabulary_pairs
        SET status = %s
    WHERE collection_id = %s
    AND id = %s;
    """

    status: int = STATUS_DELETED

    params: tuple = (
        status,
        collection_id,
        pair_id
    )

    execute_commit(
        sql=sql,
        params=params
    )

# change
def change_collection(
        collection_id: int,
        columns: list[str],
        values: list
) -> None:
    set_clause: str = ", ".join(f"{col} = %s" for col in columns)
    
    sql: str = f"""
    UPDATE vocabulary_collections
    SET {set_clause}
    WHERE id = %s;
    """

    params = [*values, collection_id]

    execute_commit(
        sql=sql,
        params=tuple(params)
    )

def change_pair(
        collection_id: int,
        pair_id: int,
        columns: list[str],
        values: list
) -> None:
    set_clause: str = ", ".join(f"{col} = %s" for col in columns)
    
    sql: str = f"""
    UPDATE vocabulary_pairs
    SET {set_clause}
    WHERE collection_id = %s
    AND id = %s;
    """

    params = [*values, collection_id, pair_id]

    execute_commit(
        sql=sql,
        params=tuple(params)
    )

# update pair
def update_pair(
        collection_id: int,
        pair_id: int,
        known: bool
) -> None:
    sql: str = """
    SELECT interval
    FROM vocabulary_pairs
    WHERE collection_id = %s
    AND id = %s
    LIMIT 1;
    """

    params: tuple = (
        collection_id,
        pair_id
    )

    rows: list[tuple] = execute_query(
        sql=sql,
        params=params
    )

    interval: int = rows[0][0] if rows else None

    new_interval: int = interval + 1 if known else INTERVAL_RESET
    
    change_pair(
        collection_id=collection_id,
        pair_id=pair_id,
        columns=['interval'],
        values=[new_interval]
    )

# get next pair
def get_next_pair(
        collection_id: int
) -> tuple:
    sql: str = """
    SELECT pair_id, created_at
    FROM vocabulary_history
    WHERE collection_id = %s
    ORDER BY created_at;
    """

    rows: list[tuple] = execute_query(
        sql=sql,
        params=(collection_id,)
    )

    history: list[tuple] = rows
    last_history_ids: list[int] = [h[0] for h in history[-DATABASE_INTERVAL:]]

    sql: str = """
    SELECT id, interval
    FROM vocabulary_pairs
    WHERE collection_id = %s;
    """

    rows: list[tuple] = execute_query(
        sql=sql,
        params=(collection_id,)
    )

    pairs: list[tuple] = rows

    for pid, interv in pairs:
        if pid not in last_history_ids:
            lowest_id, lowest_interval = pid, interv
            break

    for pid, interv in pairs:
        if pid not in last_history_ids and interv < lowest_interval:
            lowest_id, lowest_interval = pid, interv

    sql: str = """
    INSERT INTO vocabulary_history
    (collection_id, pair_id)
    VALUES (%s, %s);
    """

    params: tuple = (
        collection_id,
        lowest_id
    )

    execute_commit(
        sql=sql,
        params=params
    )

    return lowest_id, lowest_interval