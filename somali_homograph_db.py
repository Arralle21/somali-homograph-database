import sqlite3
import csv

class SomaliHomographDB:
    def __init__(self, db_name='somali_homographs.db'):
        self.db_name = db_name
        self.create_database()

    def create_database(self):
        with sqlite3.connect(self.db_name) as conn:
            cursor = conn.cursor()
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS homographs (
                id INTEGER PRIMARY KEY,
                word TEXT NOT NULL UNIQUE
            )
            ''')
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS definitions (
                id INTEGER PRIMARY KEY,
                homograph_id INTEGER,
                definition TEXT NOT NULL,
                FOREIGN KEY (homograph_id) REFERENCES homographs (id)
            )
            ''')

    def insert_homograph(self, word, definitions):
        with sqlite3.connect(self.db_name) as conn:
            cursor = conn.cursor()
            try:
                cursor.execute('INSERT INTO homographs (word) VALUES (?)', (word,))
                homograph_id = cursor.lastrowid
                for definition in definitions:
                    cursor.execute('INSERT INTO definitions (homograph_id, definition) VALUES (?, ?)',
                                   (homograph_id, definition))
                return True
            except sqlite3.IntegrityError:
                print(f"Error: The word '{word}' already exists in the database.")
                return False

    def get_homograph(self, word):
        with sqlite3.connect(self.db_name) as conn:
            cursor = conn.cursor()
            cursor.execute('''
            SELECT h.word, d.definition 
            FROM homographs h
            JOIN definitions d ON h.id = d.homograph_id
            WHERE h.word = ?
            ''', (word,))
            return cursor.fetchall()

    def update_homograph(self, word, new_definitions):
        with sqlite3.connect(self.db_name) as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT id FROM homographs WHERE word = ?', (word,))
            result = cursor.fetchone()
            if result:
                homograph_id = result[0]
                cursor.execute('DELETE FROM definitions WHERE homograph_id = ?', (homograph_id,))
                for definition in new_definitions:
                    cursor.execute('INSERT INTO definitions (homograph_id, definition) VALUES (?, ?)',
                                   (homograph_id, definition))
                return True
            else:
                print(f"Error: The word '{word}' does not exist in the database.")
                return False

    def delete_homograph(self, word):
        with sqlite3.connect(self.db_name) as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT id FROM homographs WHERE word = ?', (word,))
            result = cursor.fetchone()
            if result:
                homograph_id = result[0]
                cursor.execute('DELETE FROM definitions WHERE homograph_id = ?', (homograph_id,))
                cursor.execute('DELETE FROM homographs WHERE id = ?', (homograph_id,))
                return True
            else:
                print(f"Error: The word '{word}' does not exist in the database.")
                return False

    def list_all_homographs(self):
        with sqlite3.connect(self.db_name) as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT word FROM homographs ORDER BY word')
            return [row[0] for row in cursor.fetchall()]

    def search_homographs(self, pattern):
        with sqlite3.connect(self.db_name) as conn:
            cursor = conn.cursor()
            cursor.execute('''
            SELECT DISTINCT h.word 
            FROM homographs h
            JOIN definitions d ON h.id = d.homograph_id
            WHERE h.word LIKE ? OR d.definition LIKE ?
            ORDER BY h.word
            ''', (f'%{pattern}%', f'%{pattern}%'))
            return [row[0] for row in cursor.fetchall()]

    def export_to_csv(self, filename):
        with sqlite3.connect(self.db_name) as conn:
            cursor = conn.cursor()
            cursor.execute('''
            SELECT h.word, d.definition 
            FROM homographs h
            JOIN definitions d ON h.id = d.homograph_id
            ORDER BY h.word, d.id
            ''')
            with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
                csv_writer = csv.writer(csvfile)
                csv_writer.writerow(['Word', 'Definition'])
                csv_writer.writerows(cursor.fetchall()) 
