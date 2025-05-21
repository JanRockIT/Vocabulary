from .db_components import execute_commit, execute_query, execute_query_one
from .constants import (
    DATABASE_INTERVAL,
    INTERVAL_RESET,
    INTERVAL_START,
    STATUS_COLLECTION_DEFAULT,
    STATUS_PAIR_DEFAULT,
    STATUS_DELETED
)
from typing import Optional, List, Dict, Any, Union
from datetime import datetime

# get
def get_collections() -> List[Dict[str, Any]]:
    """Holt alle Vokabelsammlungen aus der Datenbank"""
    sql: str = """
    SELECT *
    FROM vocabulary_collections
    WHERE status != %s
    ORDER BY created_at DESC;
    """
    
    try:
        return execute_query(sql, (STATUS_DELETED,))
    except Exception as e:
        print(f"Fehler beim Abrufen der Sammlungen: {e}")
        return []

def get_collection(collection_id: int) -> Optional[Dict[str, Any]]:
    """Holt eine bestimmte Vokabelsammlung anhand der ID"""
    sql: str = """
    SELECT *
    FROM vocabulary_collections
    WHERE id = %s AND status != %s
    LIMIT 1;
    """
    
    try:
        return execute_query_one(sql, (collection_id, STATUS_DELETED))
    except Exception as e:
        print(f"Fehler beim Abrufen der Sammlung {collection_id}: {e}")
        return None

def get_pairs(collection_id: int) -> List[Dict[str, Any]]:
    """Holt alle Vokabelpaare einer Sammlung"""
    sql: str = """
    SELECT vp.*
    FROM vocabulary_pairs vp
    JOIN vocabulary_collections vc ON vp.collection_id = vc.id
    WHERE vp.collection_id = %s 
    AND vp.status != %s
    AND vc.status != %s
    ORDER BY vp.next_review, vp.interval;
    """
    
    try:
        return execute_query(sql, (collection_id, STATUS_DELETED, STATUS_DELETED))
    except Exception as e:
        print(f"Fehler beim Abrufen der Vokabeln für Sammlung {collection_id}: {e}")
        return []

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
        collection_id: int
) -> list[tuple]:
    sql: str = """
    SELECT *
    FROM vocabulary_history
    WHERE collection_id = %s;
    """

    rows: list[tuple] = execute_query(
        sql=sql,
        params=(collection_id,)
    )

    return rows

# add
def add_collection(
        collection_name: str,
        source_language: str,
        target_language: str
) -> Optional[int]:
    """Fügt eine neue Vokabelsammlung hinzu"""
    sql: str = """
    INSERT INTO vocabulary_collections (
        name,
        source_language,
        target_language,
        status,
        interval,
        created_at,
        updated_at
    )
    VALUES (%(name)s, %(source_language)s, %(target_language)s, 
            %(status)s, %(interval)s, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
    RETURNING id;
    """
    
    params = {
        'name': collection_name,
        'source_language': source_language,
        'target_language': target_language,
        'status': STATUS_COLLECTION_DEFAULT,
        'interval': INTERVAL_START
    }
    
    try:
        result = execute_query_one(sql, params)
        return result['id'] if result else None
    except Exception as e:
        print(f"Fehler beim Hinzufügen der Sammlung: {e}")
        return None

def add_pair(
        collection_id: int,
        source_word: str,
        target_word: str
) -> Optional[int]:
    """Fügt ein neues Vokabelpaar zu einer Sammlung hinzu"""
    sql: str = """
    INSERT INTO vocabulary_pairs (
        collection_id,
        source_word,
        target_word,
        status,
        interval,
        created_at,
        updated_at
    )
    VALUES (%(collection_id)s, %(source_word)s, %(target_word)s, 
            %(status)s, %(interval)s, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
    RETURNING id;
    """
    
    params = {
        'collection_id': collection_id,
        'source_word': source_word.strip(),
        'target_word': target_word.strip(),
        'status': STATUS_PAIR_DEFAULT,
        'interval': INTERVAL_START
    }
    
    try:
        # Überprüfe, ob die Sammlung existiert
        collection = get_collection(collection_id)
        if not collection:
            print(f"Sammlung {collection_id} existiert nicht")
            return None
            
        result = execute_query_one(sql, params)
        return result['id'] if result else None
    except Exception as e:
        print(f"Fehler beim Hinzufügen des Vokabelpaars: {e}")
        return None

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
) -> bool:
    """
    Update the learning status of a vocabulary pair using SM-2 algorithm
    
    Args:
        collection_id: ID of the collection
        pair_id: ID of the vocabulary pair
        known: Whether the word was known or not
    
    Returns:
        bool: True if update was successful, False otherwise
    """
    from datetime import datetime, timedelta
    
    # First, get the current pair data
    sql = """
    SELECT id, interval, next_review
    FROM vocabulary_pairs
    WHERE collection_id = %s
    AND id = %s
    AND status != %s
    LIMIT 1;
    """
    
    try:
        # Get current pair data
        pair = execute_query_one(
            sql,
            (collection_id, pair_id, STATUS_DELETED)
        )
        
        if not pair:
            print(f"Pair {pair_id} not found in collection {collection_id} or already deleted")
            return False
            
        current_interval = pair.get('interval', 0)
        now = datetime.now()
        
        # SM-2 Algorithm
        if known:
            # If the word was known, increase the interval
            if current_interval == 0:
                new_interval = 1
            elif current_interval == 1:
                new_interval = 2
            elif current_interval == 2:
                new_interval = 4
            elif current_interval == 3:
                new_interval = 4
            else:  # current_interval >= 4
                new_interval = current_interval + 1
        else:
            # If the word was not known, reset the interval
            new_interval = 0
        
        # Calculate next review date based on the new interval
        if new_interval == 0:
            days_to_add = 1  # Review tomorrow
        elif new_interval == 1:
            days_to_add = 1  # 1 day later
        elif new_interval == 2:
            days_to_add = 3  # 3 days later
        elif new_interval == 3:
            days_to_add = 7  # 1 week later
        elif new_interval == 4:
            days_to_add = 14  # 2 weeks later
        else:
            days_to_add = new_interval * 7  # Number of weeks
        
        next_review = (now + timedelta(days=days_to_add)).replace(
            hour=0, minute=0, second=0, microsecond=0
        )
        
        # Update the pair with new interval and next review date
        update_sql = """
        UPDATE vocabulary_pairs
        SET 
            interval = %s,
            next_review = %s,
            updated_at = %s
        WHERE id = %s 
        AND collection_id = %s
        RETURNING id;
        """
        
        result = execute_query_one(
            update_sql,
            (
                new_interval,
                next_review,
                now,
                pair_id,
                collection_id
            )
        )
        
        if not result:
            print(f"Failed to update pair {pair_id} in collection {collection_id}")
            return False
            
        # Add to history
        try:
            add_history(collection_id, pair_id)
        except Exception as e:
            print(f"Warning: Could not add to history: {e}")
            # Don't fail if history can't be updated
            
        return True
        
    except Exception as e:
        print(f"Error in update_pair for pair {pair_id}: {str(e)}")
        print(traceback.format_exc())
        return False

# start lerning
def start_learning(
        collection_id: int
) -> None:
    sql: str = """
    UPDATE vocabulary_collections
       SET times_lerned = times_lerned + 1
     WHERE id = %s;
    """
    execute_commit(
        sql=sql,
        params=(collection_id,)
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