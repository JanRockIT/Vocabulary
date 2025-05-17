from db_functions import (
    get_collections,
    get_collection,
    get_pairs,
    get_pair,
    get_all_history,
    get_collection_history,
    add_collection,
    add_pair,
    add_history,
    delete_collection,
    delete_pair,
    change_collection,
    change_pair,
    update_pair,
    get_next_pair
)
from constants import (
    DATABASE_INTERVAL,
    INTERVAL_RESET,
    INTERVAL_START,
    STATUS_COLLECTION_DEFAULT,
    STATUS_PAIR_DEFAULT,
    STATUS_DELETED
)

def main():
    # 1) Collections anlegen
    collection_ids = []
    for i in range(1, 6):
        name = f"Unit 1, Lesson {i}"
        cid = add_collection(name, "German", "Korean")
        print(f"Created collection {cid}: {name}")
        collection_ids.append(cid)
    print("All collections:", get_collections())

    # 2) Pairs hinzufügen
    for cid in collection_ids:
        for j in range(1, 21):
            print(f"add_pair params: ({cid}, 'de_word_{j}', 'kr_word_{j}')")
            add_pair(cid, f"de_word_{j}", f"kr_word_{j}")
        print(f"Pairs for collection {cid}:", get_pairs(cid))

    # 3) History testen
    first_cid = collection_ids[0]
    first_pair_id = get_pairs(first_cid)[0][0]
    add_history(first_cid, first_pair_id)
    print("All history:", get_all_history())
    print(f"History for collection {first_cid}:", get_collection_history(first_cid))

    # 4) Collection ändern
    print("Before rename:", get_collection(first_cid))
    change_collection(first_cid, ["name"], ["Unit 1, Lesson X"])
    print("After rename:", get_collection(first_cid))

    # 5) Pair ändern
    print("Before change_pair:", get_pair(first_cid, first_pair_id))
    change_pair(first_cid, first_pair_id, ["source_word", "target_word"], ["Haus", "집"])
    print("After change_pair:", get_pair(first_cid, first_pair_id))

    # 6) update_pair
    print("Before update_pair interval:", get_pair(first_cid, first_pair_id))
    update_pair(first_cid, first_pair_id, True)
    print("After update_pair interval:", get_pair(first_cid, first_pair_id))

    # 7) get_next_pair
    next_id, next_interval = get_next_pair(first_cid)
    print("Next pair:", (next_id, next_interval))

    # 8) delete_pair
    print("Deleting pair", first_pair_id)
    delete_pair(first_cid, first_pair_id)
    print("After delete_pair:", get_pair(first_cid, first_pair_id))

    # 9) delete_collection
    print("Deleting collection", first_cid)
    delete_collection(first_cid)
    print("After delete_collection:", get_collection(first_cid))

if __name__ == "__main__":
    main()
