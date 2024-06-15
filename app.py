from flask import Flask, render_template, request, redirect, url_for
import sqlite3
import secrets

app = Flask(__name__)

# Function to generate a one-time secret
def generate_secret():
    return secrets.token_urlsafe(16)

# Route to create a new note
@app.route('/')
def index():
    secret_key = generate_secret()
    return render_template('index.html', secret_key=secret_key)

# Route to handle form submission and store the note in SQLite database
@app.route('/create_note', methods=['POST'])
def create_note():
    secret_key = request.form.get('secret_key')
    note_text = request.form.get('note_text')

    # Connect to SQLite database
    connection = sqlite3.connect('notes.db')
    cursor = connection.cursor()

    # Create notes table if not exists
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS notes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            secret_key TEXT NOT NULL,
            note_text TEXT NOT NULL,
            is_opened INTEGER DEFAULT 0
        )
    ''')

    # Insert the note into the database
    cursor.execute("INSERT INTO notes (secret_key, note_text) VALUES (?, ?)", (secret_key, note_text))
    
    # Commit the changes and close the connection
    connection.commit()
    cursor.close()
    connection.close()

    return redirect( url_for('index') + 'note/' + secret_key)


# Route to display and delete an opened note
@app.route('/open_note/<secret_key>', methods=['GET'])
def open_note(secret_key):
    # Connect to SQLite database
    connection = sqlite3.connect('notes.db')
    cursor = connection.cursor()

    # Retrieve the note and mark it as opened
    cursor.execute("SELECT * FROM notes WHERE secret_key = ? AND is_opened = 0", (secret_key,))
    note = cursor.fetchone()

    if note:
        note_id, _, note_text, _ = note

        # Mark the note as opened
        cursor.execute("UPDATE notes SET is_opened = 1 WHERE id = ?", (note_id,))

        # Commit the changes and close the connection
        connection.commit()
        cursor.close()
        connection.close()

        return render_template('open_note.html', note_text=note_text)
    else:
        return render_template("opened.html")


# Route to display and delete an opened note
@app.route('/note/<secret_key>', methods=['GET'])
def note(secret_key):
    # Connect to SQLite database
    connection = sqlite3.connect('notes.db')
    cursor = connection.cursor()

    # Retrieve the note and mark it as opened
    cursor.execute("SELECT * FROM notes WHERE secret_key = ? AND is_opened = 0", (secret_key,))
    note = cursor.fetchone()

    if note:
        note_id, _, note_text, _ = note

     

        return render_template('note.html', secret_key=secret_key)
    else:
        return render_template("opened.html")


if __name__ == '__main__':
    app.run(debug=True, port=5000)
