from flask import Flask
from flask import render_template, request, redirect, url_for, session, abort, jsonify

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


# Aashmun Gupta
@app.route('/')
def index():
    if 'username' in session and 'role' in session:
        return redirect(url_for(session['role'], username=session['username']))
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

        cur.close()

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
            session['role'] = users[8]
            if users[8] == 'Admin':
                return redirect(url_for('admin', username=username))
            if users[8] == 'Student':
                return redirect(url_for('home', username=username))
            if users[8] == 'Faculty':
                return redirect(url_for('faculty', username=username))
        cur.close()
    return render_template('login.html')


@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('login'))


@app.route('/home/<username>')
def home(username):
    if 'username' in session and session['username'] == username and session['role'] == 'Student':
        return render_template('home.html', username=username)
    return redirect(url_for('login'))


@app.route('/admin/<username>')
def admin(username):
    if 'username' in session and session['username'] == username and session['role'] == 'Admin':
        library_data = get_library_data()
        return render_template('admin/index.html', username=username)
    return redirect(url_for('login'))
#


# Dhruv Sharma
def get_library_data():
    cur = mysql.connection.cursor()
    cur.execute("SELECT library_id, exchanges, amount FROM external_library")
    library_data = cur.fetchall()
    cur.close()
    return library_data


# Aashmun Gupta
@app.route('/faculty/<username>', methods=['GET', 'POST'])
def faculty(username):
    if 'username' in session and session['username'] == username and session['role'] == 'Faculty':
        if request.method == 'POST':
            return redirect(url_for('faculty_recommend', username=username))
        return render_template('faculty.html', username=username)
    return redirect(url_for('login'))


@app.route('/faculty/<username>/recommend', methods=['GET', 'POST'])
def faculty_recommend(username):
    if 'username' in session and session['username'] == username and session['role'] == 'Faculty':
        if request.method == 'POST':
            user_id = request.form['user_id']
            course = request.form['course']
            title = request.form['title']
            catalogue = catalogue_ref(title)
            if catalogue is None:
                error = "Catalogue not found for the given title."
                return jsonify({'error': error}), 400  # Return error as JSON with status code 400
            try:
                cur = mysql.connection.cursor()
                cur.execute(
                    'INSERT INTO recommendation (user_id, catalogue_id, course_id) VALUES (%s, %s, %s)',
                    (user_id, catalogue, course,)
                )
                mysql.connection.commit()
                cur.close()
                return redirect(url_for('faculty', username=username))
            except Exception as e:
                error = "Error occurred while adding book: " + str(e)
                return jsonify({'error': error}), 500  # Return error as JSON with status code 500
        return render_template('faculty_recommend.html', username=username)
    abort(403)  # forbidden


def catalogue_ref(title):
    cur = mysql.connection.cursor()
    cur.execute(
        "SELECT catalogue_id FROM catalogue WHERE title = %s",
        (title,)
    )
    result = cur.fetchone()
    cur.close()
    return result


@app.route('/<username>/rooms', methods=['GET', 'POST'])
def rooms(username):
    if 'username' in session and session['username'] == username:
        if request.method == 'POST':
            start = request.form['start_time']
            end = request.form['end_time']
            cur = mysql.connection.cursor()
            cur.execute(
                'SELECT room_id FROM rooms WHERE leaving_time < %s OR entry_time > %s',
                (start, end,)
            )
            cur.close()
            return jsonify()
        return render_template('room_book.html')
    abort(403)  # forbidden

# Anmol Kumar
@app.route('/catalogue/search', methods=['POST'])
def search_catalogue():
    search_query = request.form['search_query']
    cur = mysql.connection.cursor()
    cur.execute(
        "SELECT title, author_id, catalogue_type, count FROM catalogue WHERE title LIKE %s",
        ('%' + search_query + '%',)
    )
    results = cur.fetchall()
    cur.close()
    catalogue_list = [{'title': result[0], 'catalogue_type': result[2]} for result in results]
    return jsonify(catalogue_list)


if __name__ == '__main__':
    app.run(debug=True)
