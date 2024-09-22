import os
from flask import Flask, jsonify, request, render_template, url_for
import sqlite3
import random
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address


app = Flask(__name__)
app.config['JSON_AS_ASCII'] = False

# Rate Limiting
limiter = Limiter(
    key_func=get_remote_address,
    default_limits=["120 per minute"]
)
limiter.init_app(app)


def get_db_connection():
    db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'fun_facts.db')
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/pretty-fact')
def pretty_fact():
    return render_template('pretty-fact.html')


@app.route('/facts/random', methods=['GET'])
@limiter.limit("120 per minute")
def get_random_fact():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT COUNT(*) FROM fun_facts')
    total_facts = cursor.fetchone()[0]

    if total_facts == 0:
        conn.close()
        return jsonify({'error': 'No facts found in the database.'}), 404

    # Retrieve all IDs
    cursor.execute('SELECT id FROM fun_facts')
    ids = [row['id'] for row in cursor.fetchall()]

    # Select a random ID
    random_id = random.choice(ids)

    cursor.execute('''
        SELECT id, fact, category, source, date_added, language, tags, author 
        FROM fun_facts 
        WHERE id = ?
    ''', (random_id,))
    fact_row = cursor.fetchone()
    conn.close()

    return jsonify({
        'id': fact_row['id'],
        'fact': fact_row['fact'],
        'category': fact_row['category'],
        'source': fact_row['source'],
        'date_added': fact_row['date_added'],
        'language': fact_row['language'],
        'tags': fact_row['tags'],
        'author': fact_row['author']
    })


@app.route('/categories', methods=['GET'])
@limiter.limit("120 per minute")
def get_categories():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT DISTINCT category FROM fun_facts WHERE category IS NOT NULL AND category != ""')
    categories = [row['category'] for row in cursor.fetchall()]
    conn.close()

    return jsonify({'categories': categories})


@app.route('/facts/random/<category>', methods=['GET'])
@limiter.limit("120 per minute")
def get_random_fact_by_category(category):
    conn = get_db_connection()
    cursor = conn.cursor()

    # Convert both the category in the database and the user's input to lowercase
    cursor.execute('SELECT COUNT(*) FROM fun_facts WHERE LOWER(category) = LOWER(?)', (category,))
    total_facts = cursor.fetchone()[0]

    if total_facts == 0:
        conn.close()
        return jsonify({'error': f'No facts found in the category "{category}".'}), 404

    cursor.execute('SELECT id FROM fun_facts WHERE LOWER(category) = LOWER(?)', (category,))
    ids = [row['id'] for row in cursor.fetchall()]

    random_id = random.choice(ids)

    cursor.execute('''
        SELECT id, fact, category, source, date_added, language, tags, author 
        FROM fun_facts 
        WHERE id = ?
    ''', (random_id,))
    fact_row = cursor.fetchone()
    conn.close()

    return jsonify({
        'id': fact_row['id'],
        'fact': fact_row['fact'],
        'category': fact_row['category'],
        'source': fact_row['source'],
        'date_added': fact_row['date_added'],
        'language': fact_row['language'],
        'tags': fact_row['tags'],
        'author': fact_row['author']
    })


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5005)
