from db_functions import (
    get_collections,
    get_collection,
    get_pairs,
    add_collection,
    add_pair,
    update_pair
)
from constants import (
    INTERVAL_RESET,
    INTERVAL_START,
    STATUS_COLLECTION_DEFAULT,
    STATUS_PAIR_DEFAULT
)

def main():
    # 1) Collection anlegen
    cid = add_collection("Unit 1, Lesson Test", "German", "Korean")
    print("New collection:", get_collection(cid))

    # 2) 10 Pairs hinzufügen
    for i in range(1, 11):
        add_pair(cid, f"de_word_{i}", f"kr_word_{i}")
    print("After add_pair:", get_collection(cid))

    # 3) Lernschritte simulieren:
    #    Wir holen alle pairs, dann identifizieren wir die IDs aus Index 5
    pairs = get_pairs(cid)
    # Simuliere, dass Pairs 1–4 gelernt werden (interval > 3)
    for pair in pairs[:4]:
        pid = pair[5]  # id steht an Position 5
        for _ in range(4):
            update_pair(cid, pid, True)

    print("After learning 4 pairs:", get_collection(cid))
    # erwartet: times_lerned = 4, percent_complete = 40.00

    # 4) Weitere drei Pairs lernen
    for pair in pairs[4:7]:
        pid = pair[5]
        for _ in range(5):
            update_pair(cid, pid, True)

    print("After learning 7 pairs:", get_collection(cid))
    # erwartet: times_lerned = 7, percent_complete = 70.00

if __name__ == "__main__":
    main()
