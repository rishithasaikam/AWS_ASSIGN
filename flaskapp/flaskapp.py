from flask import Flask, render_template, request, redirect, url_for, send_from_directory
import sqlite3
import os

app = Flask(__name__)

# SQLite setup
DATABASE = 'mydatabase.db'
UPLOAD_FOLDER = 'uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Ensure the upload directory exists
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

def init_db():
    """Initialize the SQLite database and create users table if not exists."""
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()
    c.execute('''
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT NOT NULL,
        password TEXT NOT NULL,
        firstname TEXT,
        lastname TEXT,
        email TEXT,
        file_name TEXT,
        word_count INTEGER
    );
    ''')
    conn.commit()
    conn.close()

init_db()

@app.route('/')
def index():
    """Render the registration page."""
    message = request.args.get('message')  # Get message from query parameters
    return render_template('register.html', message=message)

@app.route('/register', methods=['POST'])
def register():
    """Handle user registration and file upload."""
    username = request.form['username']
    password = request.form['password']
    firstname = request.form['firstname']
    lastname = request.form['lastname']
    email = request.form['email']
    uploaded_file = request.files.get('file')  # Safely get the file

    # Handle file upload
    if uploaded_file and uploaded_file.filename != "":
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], uploaded_file.filename)
        uploaded_file.save(file_path)
        word_count = count_words(file_path)
        file_name = uploaded_file.filename
    else:
        file_name = None
        word_count = 0  # No file means no word count

    # Insert into database
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()
    c.execute("INSERT INTO users (username, password, firstname, lastname, email, file_name, word_count) VALUES (?, ?, ?, ?, ?, ?, ?)",
              (username, password, firstname, lastname, email, file_name, word_count))
    conn.commit()
    conn.close()

    return redirect(url_for('index', message="You have successfully registered."))

@app.route('/login', methods=['GET', 'POST'])
def login():
    """Handle user login."""
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        conn = sqlite3.connect(DATABASE)
        c = conn.cursor()
        c.execute("SELECT * FROM users WHERE username=? AND password=?", (username, password))
        user = c.fetchone()
        conn.close()

        if user:
            return render_template('profile.html', user=user)
        else:
            return "Invalid credentials. Please try again."

    return render_template('login.html')

@app.route('/download/<filename>')
def download_file(filename):
    """Serve the uploaded file for download."""
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    if os.path.exists(file_path):
        return send_from_directory(app.config['UPLOAD_FOLDER'], filename, as_attachment=True)
    else:
        return "File not found", 404

def count_words(file_path):
    """Count words in a text file."""
    try:
        with open(file_path, 'r', encoding="utf-8") as file:
            content = file.read()
            return len(content.split())
    except Exception as e:
        print(f"Error reading file: {e}")
        return 0

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80, debug=True)

