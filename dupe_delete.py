import sqlite3
from rapidfuzz import fuzz
import re
import time


# List of exempt fact IDs
EXEMPT_FACTS = {8, 35, 11, 110, 79, 109, 97, 121, 125, 194, 201, 207}

def preprocess_text(text):
    return re.sub(r'[^\w\s]', '', text.lower())

# Function to calculate similarity ratio between two strings using RapidFuzz
def similarity_ratio(a, b):
    return fuzz.token_sort_ratio(a, b) / 100  # Returns a value between 0 and 1

#create indexes
def create_indexes(cursor):
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_id ON fun_facts(id);')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_date_added ON fun_facts(date_added);')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_fact ON fun_facts(fact);')

# Function to check for duplicate facts and handle deletions
def check_for_duplicates(cursor):
    cursor.execute('SELECT id, fact, date_added FROM fun_facts WHERE id NOT IN ({seq})'.format(
        seq=','.join(['?']*len(EXEMPT_FACTS))), tuple(EXEMPT_FACTS))
    facts = cursor.fetchall()

    # Preprocess all facts once and store in a list
    preprocessed_facts = []
    for fact in facts:
        id_, fact_text, date_added = fact
        preprocessed = preprocess_text(fact_text)
        preprocessed_facts.append((id_, preprocessed, fact_text, date_added))

    total_comparisons = 0
    start_time = time.perf_counter()

    print(f"Starting exhaustive duplicate check for {len(preprocessed_facts)} facts...")

    # To keep track of deleted IDs to avoid multiple deletions
    deleted_ids = set()

    n = len(preprocessed_facts)
    for i in range(n):
        id1, pre1, original1, date_added1 = preprocessed_facts[i]
        if id1 in deleted_ids:
            continue

        for j in range(i + 1, n):
            id2, pre2, original2, date_added2 = preprocessed_facts[j]
            if id2 in deleted_ids:
                continue

            total_comparisons += 1
            similarity = similarity_ratio(pre1, pre2)

            if similarity > 0.7:
                print(f"\nPotential duplicate found:")
                print(f"Fact 1 (ID {id1}): {original1}")
                print(f"Fact 2 (ID {id2}): {original2}")
                print(f"Similarity: {similarity:.2f}")

                while True:
                    choice = input(f"Do you want to delete the newer fact? (y/n): ").strip().lower()
                    if choice in {'y', 'n'}:
                        break
                    else:
                        print("Invalid input. Please enter 'y' or 'n'.")

                if choice == 'y':
                    if date_added1 > date_added2:
                        delete_id = id1
                    else:
                        delete_id = id2

                    cursor.execute('DELETE FROM fun_facts WHERE id = ?', (delete_id,))
                    deleted_ids.add(delete_id)
                    print(f"Deleted fact with ID {delete_id}.")

    end_time = time.perf_counter()
    elapsed_time = end_time - start_time
    print(f"\nExhaustive duplicate checking completed in {elapsed_time:.4f} seconds.")  # Increased decimal precision
    print(f"Total comparisons made: {total_comparisons}")

# Main execution
def main():
    conn = sqlite3.connect('fun_facts.db')
    cursor = conn.cursor()

    create_indexes(cursor)

    check_for_duplicates(cursor)

    conn.commit()
    conn.close()

    print("Process finished with exit code 0.")

if __name__ == "__main__":
    main()
