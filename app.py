from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
from flask_mysqldb import MySQL
import config

app = Flask(__name__)
app.secret_key = config.SECRET_KEY

# Configure db
app.config['MYSQL_HOST'] = config.MYSQL_HOST
app.config['MYSQL_USER'] = config.MYSQL_USER
app.config['MYSQL_PASSWORD'] = config.MYSQL_PASSWORD
app.config['MYSQL_DB'] = config.MYSQL_DB

mysql = MySQL(app)

# Function to fetch data from external library table
def get_library_data():
    cur = mysql.connection.cursor()
    cur.execute("SELECT library_id, exchanges, transaction FROM external_library")
    library_data = cur.fetchall()
    cur.close()
    return library_data

@app.route('/')
def index():
    if 'username' in session:
        return redirect(url_for('home', username=session['username']))
    return redirect(url_for('login'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        error = None
        if not username:
            error = 'Username is required.'
        elif not password:
            error = 'Password is required.'

        cur = mysql.connection.cursor()
        cur.execute('SELECT * FROM user WHERE username = %s', (username,))
        user = cur.fetchone()
        if user:
            error = 'Account already exists !'

        if error is None:
            cur.execute('INSERT INTO user (username, password) VALUES (%s, %s)', (username, password,))
            mysql.connection.commit()

        flash(error)
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        error = None
        cur = mysql.connection.cursor()
        cur.execute('SELECT * FROM user WHERE username = %s AND password = %s', (username, password))
        user = cur.fetchone()
        cur.close()
        if user:
            session['username'] = username
            if username == 'admin':
                session['is_admin'] = True
                return redirect(url_for('admin'))
            else:
                return redirect(url_for('home', username=username))
        else:
            error = 'Incorrect username / password !'
            flash(error)
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('username', None)
    session.pop('is_admin', None)
    return redirect(url_for('login'))

@app.route('/home/<username>')
def home(username):
    if 'username' in session and session['username'] == username:
        return render_template('home.html', username=username)
    return redirect(url_for('login'))

@app.route('/catalogue/search', methods=['POST'])
def search_catalogue():
    search_query = request.form['search_query']
    cur = mysql.connection.cursor()
    cur.execute("SELECT title, author_id, catalogue_type, count FROM catalogue WHERE title LIKE %s", ('%' + search_query + '%',))
    results = cur.fetchall()
    cur.close()
    catalogue_list = [{'title': result[0], 'catalogue_type': result[2]} for result in results]
    return jsonify(catalogue_list)

@app.route('/admin')
def admin():
    # Check if user is logged in as admin
    if 'is_admin' not in session:
        return redirect(url_for('admin_login'))

    # Fetch data from external library table using the function
    library_data = get_library_data()

    # Fetch data from available rooms table
    cur = mysql.connection.cursor()
    cur.execute("SELECT room_id, entry_time, leaving_time FROM rooms")
    rooms_data = cur.fetchall()
    cur.close()

    # Fetch data from catalogue table
    cur = mysql.connection.cursor()
    cur.execute("SELECT title, author_id, catalogue_type, count FROM catalogue")
    catalogue_data = cur.fetchall()
    cur.close()

    # Fetch data from shelf table
    cur = mysql.connection.cursor()
    cur.execute("SELECT category, column, status FROM shelf")
    shelf_data = cur.fetchall()
    cur.close()

    # You can process catalogue_data and shelf_data as needed and pass them to the template
    return render_template('admin.html', library_data=library_data, rooms_data=rooms_data, catalogue_data=catalogue_data, shelf_data=shelf_data)

@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        error = None
        cur = mysql.connection.cursor()
        cur.execute('SELECT * FROM user WHERE username = %s AND password = %s', (username, password))
        user = cur.fetchone()
        cur.close()
        if user and username == 'admin':
            session['username'] = username
            session['is_admin'] = True
            return redirect(url_for('admin'))
        else:
            error = 'Incorrect username or password.'
            flash(error)
    return render_template('admin_login.html')

@app.route('/admin/logout')
def admin_logout():
    session.pop('is_admin', None)
    return redirect(url_for('admin_login'))
