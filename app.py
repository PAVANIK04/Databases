from flask import Flask
from flask import render_template, request, redirect, url_for, session, flash, jsonify

from flask_sqlalchemy import SQLAlchemy
from flask_mysqldb import MySQL

import config

app = Flask(__name__)
app.secret_key = config.SECRET_KEY

# # Creating SQLAlchemy instance
# db = SQLAlchemy()

# Configure db
app.config['MYSQL_HOST'] = config.MYSQL_HOST
app.config['MYSQL_USER'] = config.MYSQL_USER
app.config['MYSQL_PASSWORD'] = config.MYSQL_PASSWORD
app.config['MYSQL_DB'] = config.MYSQL_DB

mysql = MySQL(app)


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
        cur.execute(
            'SELECT * FROM user WHERE username = %s', (username,)
        )
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
        cur.execute(
            'SELECT * FROM user WHERE username = %s AND password = %s', (username, password)
        )
        users = cur.fetchone()
        if users is None:
            error = 'Incorrect username / password !'
        if error is None:
            session['username'] = username
            return redirect(url_for('home', username=username))
        flash(error)
    return render_template('login.html')


@app.route('/logout')
def logout():
    session.pop('username', None)
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

@app.route('/admin')
def admin():
    # Check if user is logged in as admin
    if 'admin_username' not in session:
        return redirect(url_for('admin_login'))
    
    # Fetch data from external library table using the function
    library_data = get_library_data()
    
    # Fetch data from available rooms table
    cur = mysql.connection.cursor()
    cur.execute("SELECT room_id, entry_time, leaving_time FROM available_rooms")
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

@app.route('/admin/check_room_availability', methods=['POST'])
def check_room_availability():
    if 'admin_username' not in session:
        return redirect(url_for('admin_login'))
    
    if request.method == 'POST':
        entry_time = request.form['entry_time']
        leaving_time = request.form['leaving_time']
        
        # Fetch available rooms within the specified time slot
        cur = mysql.connection.cursor()
        cur.execute("SELECT room_id FROM available_rooms WHERE entry_time <= %s AND leaving_time >= %s", (leaving_time, entry_time))
        available_rooms = cur.fetchall()
        cur.close()
        
        if available_rooms:
            flash('Rooms are available for the selected time slot.')
        else:
            flash('No rooms available for the selected time slot.')
    
    return redirect(url_for('admin'))

@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        error = None
        cur = mysql.connection.cursor()
        cur.execute(
            'SELECT * FROM admin WHERE username = %s AND password = %s', (username, password)
        )
        user = cur.fetchone()
        cur.close()
        if user:
            session['admin_username'] = username
            return redirect(url_for('admin'))
        else:
            error = 'Incorrect username or password.'
            flash(error)
    return render_template('admin_login.html')

@app.route('/admin/logout')
def admin_logout():
    session.pop('admin_username', None)
    return redirect(url_for('admin_login'))

if __name__ == '__main__':
    app.run(debug=True)
